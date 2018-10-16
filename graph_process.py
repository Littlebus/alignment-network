import random


def selectAnchorLink(percent, S, T):
    '''
    :percent: 保留anchor link的比例
    :S: 源网络的文件位置
    :T: 目标网络的文件位置
    :return: (S',T')的邻接矩阵
    '''
    usr_list_s = set()
    usr_list_t = set()
    with open(S, 'r') as fin:
        for eachline in fin:
            usr_list_s.add(eachline.split('\t')[0])
            usr_list_s.add(eachline.split('\t')[1])
    with open(T, 'r') as fin:
        for eachline in fin:
            usr_list_t.add(eachline.split('\t')[0])
            usr_list_t.add(eachline.split('\t')[1])
    
    usr_common = usr_list_s.intersection(usr_list_t)
    return random.sample(usr_common, int(percent * len(usr_common)) // 100)

def sampleNetwork(sp, ov, per, G):
    '''
    :sparsity: 稀疏度参数
    :overlap: 重叠等级
    :G: 原始图
    :return: 采样的图,[(ui, uv), ...]
    '''
    degree_counter = {}
    sample = set()
    for edge in G:
        if edge[0] not in degree_counter:
            degree_counter[edge[0]] = [[], 0]
        if edge[1] not in degree_counter:
            degree_counter[edge[1]] = [[], 0]
        if edge[0] not in degree_counter[edge[1]][0]:
            degree_counter[edge[0]][0].append(edge[1])
            degree_counter[edge[1]][0].append(edge[0])
        else:
            degree_counter[edge[0]][1] += 1
            degree_counter[edge[1]][1] += 1
    # 筛选出度大于5的点。
    for vertex1, content in degree_counter.items():
        if content[1] >= 5:
            for vertex2 in content[0]:
                if degree_counter[vertex2][1] >= 5:
                    if vertex1 in degree_counter[vertex2][0]:
                        degree_counter[vertex2][0].remove(vertex1)
                        sample.add((vertex1, vertex2))
    
    # 按照概率采样
    graph_s = []
    graph_t = []
    anchor_s = set()
    anchor_t = set()
    for edge in sample:
        p = random.random()
        if p <= 1 - 2 * sp + sp * ov:
            continue
        elif 1 - 2 * sp + sp * ov < p and p <= 1 - sp:
            graph_s.append(edge)
            anchor_s.add(edge[0])
            anchor_s.add(edge[1])
        elif 1 - sp < p and p <= 1- sp * ov:
            graph_t.append(edge)
            anchor_t.add(edge[0])
            anchor_t.add(edge[1])
        else:
            graph_s.append(edge)
            graph_t.append(edge)
            anchor_s.add(edge[0])
            anchor_s.add(edge[1])
            anchor_t.add(edge[0])
            anchor_t.add(edge[1])
    anchor_links = list(anchor_s.intersection(anchor_t))
    rest_links = random.sample(anchor_links, int(per * len(anchor_links)))

    return graph_s, graph_t, rest_links

def crossNetworkExtension(S, T, A):
    '''
    :S: 源网络
    :T: 目标网络
    :A: anchor link集合,list
    :return: 扩展后的网络
    '''
    print(A)
    friend_list_s = {}
    friend_list_t = {}
    for edge in S:
        (u1, u2) = edge
        if u1 not in friend_list_s:
            friend_list_s[u1] = set()
        if u2 not in friend_list_s:
            friend_list_s[u2] = set()
        friend_list_s[u1].add(u2)
        friend_list_s[u2].add(u1)
    
    for edge in T:
        [u1, u2] = edge
        if u1 not in friend_list_t:
            friend_list_t[u1] = set()
        if u2 not in friend_list_t:
            friend_list_t[u2] = set()
        friend_list_t[u1].add(u2)
        friend_list_t[u2].add(u1)

    for usr in A:
        for friend in friend_list_s[usr]:
            if friend in A and friend not in friend_list_t[usr]:
                # s网络里两个anchor是朋友，在t里不是朋友
                # 进行更改，添加t里的朋友关系
                friend_list_t[friend].add(usr)
                friend_list_t[usr].add(friend)

        for friend in friend_list_t[usr]:
            if friend in A and friend not in friend_list_s[usr]:
                # t网络里两个anchor是朋友，在s里不是朋友
                # 进行更改，添加s里的朋友关系
                friend_list_s[friend].add(usr)
                friend_list_s[usr].add(friend)

    adjacency_list_s = set()
    adjacency_list_t = set()
    for usr, friends in friend_list_s.items():
        for friend in friends:
            adjacency_list_s.add((usr, friend))
            friend_list_s[friend].remove(usr)
    for usr, friends in friend_list_t.items():
        for friend in friends:
            adjacency_list_t.add((usr, friend))
            friend_list_t[friend].remove(usr)
    return list(adjacency_list_s), list(adjacency_list_t)


def loadGraph(address):
    '''
    :address: 文件路径
    :return: list，图，节点为整数
    '''
    graph = set()
    with open(address, 'r') as fin:
        for eachline in fin:
            [ui, uj] = eachline.split('\t')[:2]
            graph.add((int(ui), int(uj)))
    return list(graph)

if __name__ == '__main__':
    main()