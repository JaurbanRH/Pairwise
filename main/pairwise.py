"""Pairwise class"""
import csv
import itertools
import math
from pprint import pprint


# pylint: disable=too-many-instance-attributes
class Pairwise:
    """Pairwise configurations generator"""

    def __init__(self, parameters, margin):
        self.configurations = []
        self.finished_parameters = set()
        self.parameters = parameters["Parameters"]
        self.weights = parameters.get("Weights", {})
        self.only_pairwise = [k for k, v in self.weights.items() if v == 0]
        self.parameters_ratio = self._create_ratio()
        self.pairs = self._generate_pairs()
        self.margin = margin if margin is not None else 0.05

    def _create_ratio(self):
        """
        :return: Dictionary with expected ratios for each parameter
        """
        parameters_ratio = {}
        ratio_sum = {}
        for kind in self.parameters:
            ratio_sum[kind] = 0
            parameters_ratio[kind] = {}
            for param in self.parameters[kind]:
                parameters_ratio[kind][param] = self.weights.get(param) if self.weights.get(param) else 1
                ratio_sum[kind] += parameters_ratio[kind][param]

        for kind, parameters in parameters_ratio.items():
            for param in parameters:
                parameters[param] /= ratio_sum[kind]
        return parameters_ratio

    def _generate_pairs(self):
        """
        :return: All possible pairs from given parameters
        """
        pairs = []
        parameter_pairs = list(itertools.combinations(self.parameters, 2))

        for param1, param2 in parameter_pairs:
            for value1 in self.parameters[param1]:
                for value2 in self.parameters[param2]:
                    pairs.append({value1, value2})

        return pairs

    def generate_configurations(self):
        """Generate all pairwise configurations for given parameters"""
        ratio_done = False

        while self.pairs or not ratio_done:
            if not self._generate_configuration():
                return False
            self._check_finished_kind()
            if not self.pairs:
                ratio_done = self._check_ratio()
        return True

    def to_csv(self, output):
        """
        :param output: Output file
        Generate CSV file containing generated configurations
        """
        writer = csv.writer(output)
        writer.writerow(self.configurations[0].keys())
        for conf in self.configurations:
            writer.writerow(conf.values())
        output.close()

    def print_quantity(self):
        """Print quantity of each parameter in generated configurations"""
        quantity = self._count_quantity()
        pprint(sorted(quantity.items(), key=lambda x: x[1]))

    def print_configurations(self):
        """Print generated configurations"""
        for i, conf in enumerate(self.configurations):
            print(f"{i + 1}: {list(conf.values())}")

    def _count_quantity(self):
        """
        :return: Quantity of each parameter in current configurations
        """
        quantity = {}
        for conf in self.configurations:
            for param in conf.values():
                if quantity.get(param):
                    quantity[param] += 1
                else:
                    quantity[param] = 1

        return quantity

    def _generate_configuration(self):
        """Generate next configuration in pairwise"""
        configuration = dict.fromkeys(self.parameters.keys())
        param_quantity = self._parameter_quantity()
        sorted_params = list(sorted(param_quantity, key=param_quantity.get))
        sorted_params.reverse()
        is_not_complete = True
        kind_numerosity = list(sorted(self.parameters, key=lambda x: len(self.parameters.get(x))))
        kind_numerosity.reverse()

        if self.pairs:
            param = self._next_param(kind_numerosity, sorted_params)
        else:
            param = self._next_quantity_param()
        main_param = param
        position = self._get_kind(param)
        while is_not_complete:
            self._update_pairs(configuration)
            configuration[position] = param

            if self._add_triplet(param, configuration, sorted_params):
                continue
            if self._add_transitive_triplet(configuration, param, sorted_params):
                continue
            if self._add_any_triplet(configuration, param, sorted_params):
                continue

            for sorted_param in sorted_params:
                if sorted_param != param:
                    if not configuration.get(self._get_kind(sorted_param)) and {param, sorted_param} in self.pairs:
                        configuration[self._get_kind(sorted_param)] = sorted_param
                        break

            self._update_pairs(configuration)
            for k, v in configuration.items():
                if not v:
                    position = k
                    break

            param = self._param_in_pair(sorted_params, self.pairs, position)
            if param is None:
                param = self._param_not_in_pair(position, sorted_params)
            is_not_complete = None in configuration.values()

        return self._add_configuration(configuration, main_param)

    def _add_configuration(self, configuration, main_param):
        """
        Add configuration to list of all configurations
        :param configuration: Generated configuration
        :param main_param: Parameter from which was configuration created
        :return: True if configuration was added to list of all generated configurations, False otherwise
        """
        if configuration not in self.configurations:
            self.configurations.append(configuration)
        else:
            if conf := self._alter_configuration(configuration):
                self.configurations.append(conf)
            else:
                conf = self._create_configuration(main_param)
                if conf:
                    self.configurations.append(conf)
                else:
                    return False
        return True

    def _param_not_in_pair(self, position, sorted_params):
        """
        Add parameter that is not in any untested pair to configuration
        :param position: Position of given parameter
        :param sorted_params: List of parameters sorted by parameter quantity
        :return: Parameter to be added to generated configuration
        """
        quantity = {}
        param = None
        if position in self.finished_parameters:
            for conf in self.configurations:
                if quantity.get(conf[position]):
                    quantity[conf[position]] += 1
                else:
                    quantity[conf[position]] = 1
            for key in quantity:
                quantity[key] /= self.weights.get(key) if self.weights.get(key) else 1
            sorted_quantity = sorted(quantity, key=quantity.get)
            for sorted_param in sorted_quantity:
                if sorted_param in self.only_pairwise and self._check_finished_param(sorted_param):
                    continue
                param = sorted_param
                break
        else:
            for sorted_param in sorted_params:
                if self._get_kind(sorted_param) == position:
                    if sorted_param in self.only_pairwise and self._check_finished_param(sorted_param):
                        continue
                    param = sorted_param
                    break
        return param

    def _update_pairs(self, configuration):
        """
        Remove pairs tested by configuration from list of all pairs
        :param configuration: Generated configuration
        """
        used_pairs = [{a, b} for a in configuration.values() for b in configuration.values()]
        self.pairs = [key for key in self.pairs if key not in used_pairs]

    def _parameter_quantity(self):
        """
        :return: Count of how many times is each parameter in remaining pairs
        """
        quantity = {}
        for value in self.parameters.values():
            for param in value:
                quantity[param] = 0

        for combination in self.pairs:
            for param in combination:
                quantity[param] += 1

        return quantity

    def _next_quantity_param(self):
        """
        :return: Parameter from which next configuration is supposed to be created
        """
        quantity = self._count_quantity()
        for kind in self.parameters_ratio.values():
            for param, value in kind.items():
                quantity[param] /= value
        sorted_quantity = sorted(quantity, key=quantity.get)
        for param in sorted_quantity:
            if param in self.only_pairwise and self._check_finished_param(param):
                continue
            return param

    def _next_param(self, kind_numerosity, sorted_params):
        """
        :param kind_numerosity: Numerosity of each parameter kind
        :param sorted_params: List of parameters sorted by quantity
        :return: Parameter from which next configuration is supposed to be created
        """
        finished_kind = None
        for kind in kind_numerosity:
            if kind not in self.finished_parameters:
                finished_kind = kind
                break
        for parameter in sorted_params:
            if self._get_kind(parameter) is finished_kind:
                if parameter in self.only_pairwise and self._check_finished_param(parameter):
                    continue
                return parameter
        print("1")
        return None

    def _check_finished_kind(self):
        """
        :return: List of parameters that are all covered at least once (are finished)
        """
        for kind in self.parameters:
            is_finished = True
            for param in self.parameters[kind]:
                is_finished = self._check_finished_param(param)
                if not is_finished:
                    break
            if is_finished:
                self.finished_parameters.add(kind)

    def _check_finished_param(self, param):
        """
        Checks if pairwise is covered for given parameter
        :param param:
        :return: True if parameter is finished, False otherwise
        """
        is_finished = True
        for pair in self.pairs:
            if param in pair:
                is_finished = False
                break
        return is_finished

    def _check_ratio(self):
        """
        :return: True when all configurations meet the ratio requirements, False otherwise
        """
        kld = self._kl_divergence()
        for ratio in kld.values():
            if self.margin == 0 and ratio != self.margin:
                return False
            if self.margin != 0 and abs(ratio) > self.margin:
                return False
        return True

    def _kl_divergence(self):
        """
        :return: KL divergence for each parameter
        """
        current_ratio = self._count_ratio()
        kld = {}
        for param, ratio in current_ratio.items():
            kld[param] = ratio * math.log(ratio / self.parameters_ratio[self._get_kind(param)][param])
        return kld

    def _count_ratio(self):
        """
        :return: Current ratio for each parameter
        """
        quantity = self._count_quantity()
        kind_sum = {}
        ratio = {}
        for kind in self.parameters:
            kind_sum[kind] = 0
            for param in self.parameters[kind]:
                kind_sum[kind] += quantity[param]
        for param, param_quantity in quantity.items():
            ratio[param] = param_quantity / kind_sum[self._get_kind(param)]
        return ratio

    def _get_kind(self, param):
        """
        :param param:
        :return Kind of given parameter
        """
        for key, value in self.parameters.items():
            if param in value:
                return key
        return None

    def _add_triplet(self, param, configuration, sorted_params):
        """
        Add (A,B,C) triplet of parameters to final configuration based on logic that
        (A,B), (B,C) and (A,C) pairs are in remaining pairs
        :param param:
        :param configuration: Generated configuration
        :param sorted_params: List of parameters sorted by quantity
        :return: True if 2 other params were added to configuration, False otherwise.
        """
        for second_param in sorted_params:
            if (
                second_param != param
                and not configuration.get(self._get_kind(second_param))
                and {param, second_param} in self.pairs
            ):
                third_param = self._find_triplet(param, second_param, configuration)
                if third_param is None:
                    continue
                configuration[self._get_kind(second_param)] = second_param
                configuration[self._get_kind(third_param)] = third_param
                return True
        return False

    def _find_triplet(self, param, second_param, configuration):
        """
        Find (A,B,C) triplet of parameters to final configuration based on logic that
        (A,B), (B,C) and (A,C) pairs are in remaining pairs
        :param param:
        :param second_param:
        :param configuration: Generated configuration
        :return: 2 parameters to be added to generated configurations if they meet requirements, None otherwise
        """
        for remaining_param in self.pairs:
            if param in remaining_param:
                copy = remaining_param.copy()
                copy.remove(param)
                third_param = copy.pop()
                if (
                    {third_param, second_param} in self.pairs
                    and {
                        third_param,
                        param,
                    }
                    in self.pairs
                    and not configuration.get(self._get_kind(third_param))
                ):
                    add = True
                    for value in configuration.values():
                        if value and (
                            {value, second_param} not in self.pairs
                            or {
                                value,
                                third_param,
                            }
                            not in self.pairs
                        ):
                            add = False
                            break
                    if add:
                        return third_param
        return None

    def _add_transitive_triplet(self, configuration, param, sorted_params):
        """
        Add (A,B,C) triplet of parameters to final configuration based on logic that
        (A,B) and (A,C) or (A,B) and (B,C) pairs are in remaining pairs
        :param configuration: Generated configuration
        :param param:
        :param sorted_params: List of parameters sorted by quantity
        :return: True if 2 other params were added to configuration, False otherwise.
        """
        for sorted_param in sorted_params:
            if sorted_param != param and (
                not configuration.get(self._get_kind(sorted_param)) and {param, sorted_param} in self.pairs
            ):
                remaining_pairs = self.pairs.copy()
                remaining_pairs.remove({param, sorted_param})
                for remaining_param in remaining_pairs:
                    # A being the main param this part looks for (A,B) and (A,C)
                    if param in remaining_param:
                        copy = remaining_param.copy()
                        copy.remove(param)
                        second_param = copy.pop()
                        if self._check_transitive_triplet(param, sorted_param, second_param, configuration):
                            return True
                        continue
                    # A being the main param this part looks for (A,B) and (B,C)
                    if sorted_param in remaining_param:
                        copy = remaining_param.copy()
                        copy.remove(sorted_param)
                        second_param = copy.pop()
                        if self._check_transitive_triplet(param, sorted_param, second_param, configuration):
                            return True
                        continue
        return False

    def _check_transitive_triplet(self, param, sorted_param, second_param, configuration):
        """
        Checks transitive triplet and add it to final configuration
        :param param:
        :param sorted_param:
        :param second_param:
        :param configuration: Generated configuration
        :return: True if 2 other params were added to configuration, False otherwise
        """
        if (
            self._get_kind(param) == self._get_kind(sorted_param)
            or self._get_kind(param) == self._get_kind(second_param)
            or self._get_kind(sorted_param) == self._get_kind(second_param)
        ):
            return False
        if {second_param, sorted_param} in self.pairs or {
            second_param,
            param,
        } in self.pairs:
            if not configuration.get(self._get_kind(second_param)):
                configuration[self._get_kind(sorted_param)] = sorted_param
                configuration[self._get_kind(second_param)] = second_param
                return True
        return False

    def _add_any_triplet(self, configuration, param, sorted_params):
        """
        Parameter A being the main parameter this function add (B,C,D) triplet of parameters to final
        configuration based on logic that (B,C), (C,D) and (B,D) pairs are in remaining pairs
        :param configuration: Generated configuration
        :param param:
        :param sorted_params: List of parameters sorted by quantity
        :return: True if 2 other params were added to configuration, False otherwise.
        """
        for sorted_param in sorted_params:
            if sorted_param != param:
                if result := self._add_triplet(param, configuration, sorted_params):
                    configuration[self._get_kind(sorted_param)] = sorted_param
                    return result
        return None

    def _param_in_pair(self, sorted_params, pairs, position):
        """
         A being the main parameter this function returns parameter B based
         on logic that (A,B) pair is in remaining pairs
        :param sorted_params: List of parameters sorted by quantity
        :param pairs: List of uncovered pairs
        :param position: Position at which the parameter should be
        :return: Parameter, if any parameter meets the requirements, None otherwise
        """
        for sorted_param in sorted_params:
            if self._get_kind(sorted_param) == position:
                for unused_pair in pairs:
                    if sorted_param in unused_pair:
                        return sorted_param
        return None

    def _alter_configuration(self, configuration):
        """
        :param configuration: Generated configuration
        :return: Altered configuration that is currently not in all created configurations
        """
        kld = self._kl_divergence()
        kld = sorted(kld, key=kld.get)
        for param in kld:
            if param in self.only_pairwise and self._check_finished_param(param):
                continue
            position = self._get_kind(param)
            tmp_conf = configuration.copy()
            tmp_conf[position] = param
            if tmp_conf not in self.configurations:
                return tmp_conf
        return None

    def _create_configuration(self, parameter):
        """
        Create configuration that is based on current quantity and ratios
        :param parameter: Main parameter from which configuration will be generated
        :return Generated configuration
        """

        def get_priority(configuration, kld):
            """
            :param configuration: Generated configuration
            :param kld: list of KL divergences for each parameter
            :return: Priority for given configuration
            """
            priority = 0
            for parameter in configuration:
                priority += kld[parameter]
            return priority

        position = self._get_kind(parameter)
        product_params = [[parameter]]
        for kind, params in self.parameters.items():
            if kind != position:
                product_params.append(params)

        product = list(itertools.product(*product_params))
        kld = self._kl_divergence()
        product.sort(key=lambda x: get_priority(x, kld))

        for conf in product:
            conf_dict = {}
            for param in conf:
                conf_dict[self._get_kind(param)] = param
            can_add = True
            for param in self.only_pairwise:
                if self._check_finished_param(param) and param in conf:
                    can_add = False
                    break
            if conf_dict not in self.configurations and can_add:
                return conf_dict
