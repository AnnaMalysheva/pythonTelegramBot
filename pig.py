n = int(input())
W = [set() for i in range(n + 1)]

for i in range(1, n+1):
    u = int(input())
    W[u].add(i)

Color = [0] * (n + 1)

CycleFound = 0


def DFS(start):
    global CycleFound
    Color[start] = 1
    for u in W[start]:
        if Color[u] == 0:
            DFS(u)
        elif Color[start] == 1:
            CycleFound += 1
        Color[start] = 2


for i in range(1, n + 1):
    if Color[i] == 0:
        DFS(i)

print(CycleFound)
