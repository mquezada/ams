from sqlalchemy import create_engine
from pathlib import Path

engine = create_engine('mysql://root@localhost/ams?charset=utf8mb4', encoding='utf-8')
engine_oracle = create_engine('mysql://root:oracle_753@localhost/ams')
engine_m3 = create_engine('mysql://mquezada:phoophoh7ahdaiJahphoh3aicooz7uka3ahJe9oi@127.0.0.1/mquezada_db')


DATA_DIR = Path('data')
LOCAL_DATA_DIR = Path('/Users', 'mquezada', 'phd', 'AMS', 'data')


class Datasets:
    oscar_pistorius = [13472, 15641, 15724, 15749, 15753, 15764, 15778, 15846, 15866, 15943, 15958, 15995, 15996, 16000,
                       16024, 16032, 16034, 16109, 16111, 16145, 16186, 16277, 16292, 16347, 16695, 16700, 16702, 16703,
                       16705, 16729, 16730, 16735, 17140, 17211, 17281, 17533, 17796, 17914, 18469, 18607, 18703, 19115,
                       19119, 19127, 20376, 20415, 20421, 20425, 20441, 20444, 20466, 20556, 20573, 20576, 20582, 20612,
                       20651, 20701, 20702, 20711, 20717, 20841, 20844, 20853, 20985, 20989, 21356, 21358, 21362, 21373,
                       21381, 21495, 21501, 21512, 21514, 21642, 21687, 21733, 21782, 24164, 24165, 24179, 24185, 24198,
                       24311, 24581, 24728, 25106, 25117, 25238, 25263, 25370, 25380, 25387, 25391, 26173, 26177, 26179,
                       27024, 27026, 31659, 31749, 31750, 31753, 31759, 31892, 32033, 32233, 32624, 32699, 36246, 36253,
                       36881, 36882, 36892, 36898, 36899, 36904, 36917, 37042, 37058]

    microsoft_nokia = [91, 92, 150, 736, 876, 1516, 1584, 22356, 22850, 22900, 23349]

    mumbai_rape = [195, 272, 863, 1749, 38]

    # mumbai2 = [38]
    libya_hotel = [43911, 43914, 43924, 43926, 43928, 43976, 43924]
    nepal_earthquake = [56739, 56745, 56748, 56750, 56754, 56756, 56758, 56761, 56762, 56763, 56764, 56767, 56769,
                       56774, 56775, 56776, 56778, 56779, 56780, 56782, 56783, 56784, 56786, 56787, 56788, 56789,
                       56790, 56791, 56795, 56797, 56799, 56800, 56801, 56803, 56804, 56805, 56807, 56809, 56811,
                       56812, 56813, 56817, 56823, 56827, 56828, 56830, 56831, 56835, 56840, 56841, 56842, 56844,
                       56846, 56752, 56772, 56796, 56798, 56810]

    # using available data
    # nepal_earthquake = [56837,
    #                     56766,
    #                     56802,
    #                     56771,
    #                     56988,
    #                     56993,
    #                     56986,
    #                     56904,
    #                     56863,
    #                     57011,
    #                     57094,
    #                     57044,
    #                     57001,
    #                     57061,
    #                     57183,
    #                     57180,
    #                     57943,
    #                     57915,
    #                     57900,
    #                     58030]
