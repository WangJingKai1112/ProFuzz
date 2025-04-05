from tree_sitter import Language, Parser
from Step3_Crossover.ast_information import extract_func_and_decl, get_swap_list
from Step3_Crossover.ast_operation import select_nodes, get_var_and_decl_info, rename_nodes, cross_nodes
from Utils.file_utils import write_log


parser = Parser()
parser.set_language(Language("Libs/tree_sitter/parser/my-languages.so", "c"))
log_path = "log.txt"


def process(population: list, pair: list) -> list:
    """
    Performs crossover between two parent programs to produce offspring.
    """
    parent_1, parent_2 = population[pair[0]], population[pair[1]]

    tree_1, tree_2 = parser.parse(parent_1.encode()), parser.parse(parent_2.encode())
    root_1, root_2 = tree_1.root_node, tree_2.root_node

    func_def_1, global_decl_1 = extract_func_and_decl(root_1)
    func_def_2, global_decl_2 = extract_func_and_decl(root_2)

    swap_list_1, swap_list_2 = get_swap_list(func_def_1), get_swap_list(func_def_2)

    select_1, select_2 = select_nodes(swap_list_1, swap_list_2)
    if select_1 is None or select_2 is None:
        write_log(log_path, f"idx = {pair}, can't find the same type of node, return parents.\n")
        return [parent_1, parent_2]

    var_all_1, decl_all_1 = get_var_and_decl_info(func_def_1[select_1[0]], global_decl_1, select_1[1], parent_1)
    var_all_2, decl_all_2 = get_var_and_decl_info(func_def_2[select_2[0]], global_decl_2, select_2[1], parent_2)

    decl_1, cross_segment_1 = rename_nodes(var_all_2, decl_all_1, select_1[1], parent_1)
    decl_2, cross_segment_2 = rename_nodes(var_all_1, decl_all_2, select_2[1], parent_2)

    offspring_1 = cross_nodes(parent_1, select_1[1], func_def_1[select_1[0]], cross_segment_2, decl_2)
    offspring_2 = cross_nodes(parent_2, select_2[1], func_def_2[select_2[0]], cross_segment_1, decl_1)
    return [offspring_1, offspring_2]


def crossover(population: list, pairs: list, offspring: list = [], reboot_idx: list = []) -> list:
    """
    Perform crossover on the population.
    """
    results = []
    for pair in pairs:
        results.extend(process(population, pair))
    if reboot_idx == []:
        write_log(log_path, f"Step3 finished. Performed crossover on {len(results)} programs (normal).\n")
        return results
    else:
        assert len(reboot_idx) <= len(offspring)
        for i in range(len(reboot_idx)):
            offspring[reboot_idx[i]] = results[i]
        write_log(log_path, f"Step3 finished. Performed crossover on {len(reboot_idx)} programs (reboot).\n")
        return offspring