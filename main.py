def read_unoriented(file : str) -> Dict[int, List[int]] :
    dict = {}
    with open(file) as f:
        for line in f:
            if line[0] == "%" :
                continue
            (key, val) = line.split()[0:2] #
            key = int(key)
            val = int(val)
            if key not in dict:
                dict[key] = list()
            dict[key].append(val)
            if val not in dict:
                dict[val] = list()
            dict[val].append(key)
    return dict