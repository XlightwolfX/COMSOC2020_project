from itertools import permutations


def p0(a, pref):
    return True


def p1(a, b, pref):
    return pref.index(a) < pref.index(b)


def p2(a, b, c, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(a) < pref.index(c))


def p3(a, b, c, pref):
    return (pref.index(b) < pref.index(a)) and (pref.index(c) < pref.index(a))


def p4(a, b, c, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(b) < pref.index(c))


def p5(a, b, c, d, pref):
    return (pref.index(a) < pref.index(c)) and (pref.index(b) < pref.index(d))


def p6(a, b, c, d, pref):
    return (pref.index(a) < pref.index(c)) and (pref.index(b) < pref.index(d)) and (pref.index(a) < pref.index(d))


def p7(a, b, c, d, pref):
    return (pref.index(a) < pref.index(c)) and (pref.index(b) < pref.index(d)) and (pref.index(a) < pref.index(d)) and (pref.index(b) < pref.index(c))


def p8(a, b, c, d, pref):
    return (pref.index(a) < pref.index(c)) and (pref.index(b) < pref.index(c)) and (pref.index(c) < pref.index(d))


def p9(a, b, c, d, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(b) < pref.index(c)) and (pref.index(b) < pref.index(d))


def p10(a, b, c, d, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(a) < pref.index(c)) and (pref.index(b) < pref.index(d)) and (pref.index(c) < pref.index(d))


def p11(a, b, c, d, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(b) < pref.index(d)) and (pref.index(c) < pref.index(d))


def p12(a, b, c, d, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(a) < pref.index(c)) and (pref.index(b) < pref.index(d))


def p13(a, b, c, d, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(a) < pref.index(c)) and (pref.index(a) < pref.index(d))


def p14(a, b, c, d, pref):
    return (pref.index(b) < pref.index(a)) and (pref.index(c) < pref.index(a)) and (pref.index(d) < pref.index(a))


def p15(a, b, c, d, pref):
    return (pref.index(a) < pref.index(b)) and (pref.index(b) < pref.index(c)) and (pref.index(c) < pref.index(d))


def main():
    total_orders = [list(x) for x in permutations([1, 2, 3, 4])]
    print('p0:', sum([p0(3, x) for x in total_orders]), '/', '24')
    print('p1:', sum([p1(3, 2, x) for x in total_orders]), '/', '24')
    print('p2:', sum([p2(1, 2, 3, x) for x in total_orders]), '/', '24')
    print('p3:', sum([p3(1, 2, 3, x) for x in total_orders]), '/', '24')
    print('p4:', sum([p4(1, 2, 3, x) for x in total_orders]), '/', '24')
    print('p5:', sum([p5(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p6:', sum([p6(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p7:', sum([p7(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p8:', sum([p8(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p9:', sum([p9(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p10:', sum([p10(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p11:', sum([p11(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p12:', sum([p12(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p13:', sum([p13(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p14:', sum([p14(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    print('p15:', sum([p15(1, 2, 3, 4, x) for x in total_orders]), '/', '24')
    num_partials = {p0: 1, p1: 12, p2: 12, p3: 12, p4: 24, p5: 12, p6: 24, p7: 6, p8: 12, p9: 12, p10: 12, p11: 24, p12: 24, p13: 4, p14: 4, p15: 24}
    indecisivness = {24: [p0], 12: [p1], 8: [p2, p3], 6: [p5, p13, p14], 5: [p6], 4: [p4, p7], 3: [p11, p12], 2: [p8, p9, p10], 1: [p15]}

    checksum = 0
    for k, v in indecisivness.items():
        indec = k / 24
        prob = sum([num_partials[vv] for vv in v]) / 219
        print(indec, ': ', prob)
        checksum += prob
    print(checksum)





if __name__ == '__main__':
    main()
