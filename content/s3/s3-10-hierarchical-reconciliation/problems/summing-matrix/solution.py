import numpy as np
from collections import deque


def summing_matrix(children, root):
    # leaves below each node, found with a depth-first search (keeps left-to-right order)
    def leaves_of(node):
        kids = children.get(node, [])
        if not kids:
            return [node]
        out = []
        for k in kids:
            out += leaves_of(k)
        return out

    leaves = leaves_of(root)
    col = {name: j for j, name in enumerate(leaves)}

    rows, queue = [], deque([root])                  # breadth-first order for the rows
    while queue:
        node = queue.popleft()
        rows.append(node)
        queue.extend(children.get(node, []))

    S = []
    for node in rows:
        row = [0] * len(leaves)
        for leaf in leaves_of(node):
            row[col[leaf]] = 1
        S.append(row)
    return {"rows": rows, "leaves": leaves, "S": S}


def bottom_up(S, bottom_forecast):
    return np.asarray(S, dtype=float) @ np.asarray(bottom_forecast, dtype=float)
