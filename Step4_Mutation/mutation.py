import torch
from tree_sitter import Language, Parser
from Step4_Mutation.graph_information import vertex_info
from Step4_Mutation.graph_mutation import graphInfo, graphMutaton
from Step4_Mutation.graph_neighbor import get_neighbors
from Utils.file_utils import write_log


parser = Parser()
parser.set_language(Language("Libs/tree_sitter/parser/my-languages.so", "c"))
log_path = "log.txt"


def process(code: str, mutation_steps: int) -> str:
    """
    Perform mutation on a single program.
    """
    factors, vertex_num, vertex_type, subgraph_type, initial_vertex = vertex_info(code)
    if factors == 0:
        return code
    objective = graphInfo(factors, vertex_num, vertex_type, subgraph_type, initial_vertex)
    adjacency_matrix = objective.adjacency_matrix
    L_known = objective.suggest_init
    for i in range(5):
        for _ in range(mutation_steps):
            neighbors = get_neighbors(L_known, adjacency_matrix, True)
            if neighbors.size(0) > 0:
                suggestion = neighbors[torch.randint(0, neighbors.size(0), (1,)).item()].unsqueeze(0)
                L_known = torch.cat([L_known, suggestion], dim = 0)
            else:
                suggestion = L_known[torch.randint(0, L_known.size(0), (1,)).item()].unsqueeze(0)

        ret = graphMutaton(code, parser.parse(code.encode()), vertex_num, vertex_type, suggestion[0])
        ret.mutate(parser.parse(code.encode()).root_node)
        if ret.code != "":
            return ret.code
        if ret.code == "" and i == 4:
            return code


def mutation(population: list, mutation_steps: int, reboot_idx: list = []) -> list:
    """
    Perform mutation on the population.
    """
    results = []
    if reboot_idx == []:
        for i in population:
            results.append(process(i, mutation_steps))
        write_log(log_path, f"Step4 finished. Performed mutation on {len(results)} programs (normal).\n")
    else:
        for i in range(len(population)):
            if i in reboot_idx:
                results.append(process(population[i], mutation_steps))
            else:
                results.append(population[i])
        write_log(log_path, f"Step4 finished. Performed mutation on {len(results)} programs (reboot).\n")
    return results