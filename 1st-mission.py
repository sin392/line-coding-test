
# constant value
from typing import Mapping


INITIAL_COST = 410
INITIAL_BORDER = 1052  # m

ADDITIONAL_COST_UNIT = 80
ADDITIONAL_BORDER = 237  # km

LOW_SPEED_UPPER_LIMIT = 10 * 1000 / 3600  # m/s
LOW_SPEED_TIME_UNIT = 90  # s
LOW_SPEED_COST_UNIT = 80

MIDNIGHT_S = 22
MIDNIGHT_E = MIDNIGHT_S + 5
MIDNIGHT_DISTANCE_RATIO = 1.25


# 深夜料金については距離の増加という形で表現される
def _process_midnight_section(times: list, distances: list) -> list:
    return [d * MIDNIGHT_DISTANCE_RATIO if int(t[0:2]) >= MIDNIGHT_S and int(t[0:2]) < MIDNIGHT_E else d for t, d in zip(times, distances)]


def _time_to_total_sec(time: str) -> float:
    hh, mm, ss = [float(x) for x in time.split(':')]
    return (hh / 3600) + (mm / 60) + ss


def _compute_time_diffs(times: list) -> list:
    res = []
    for i in range(len(times)):
        if i == 0:
            res.append(0)
        else:
            res.append(_time_to_total_sec(
                times[i]) - _time_to_total_sec(times[i-1]))
    return res


# テストのためには要素用の関数の方がいいが時間の差分が必要なので
# times[0]はスタート時で距離0 -> 速度も0なのでそのまま
def _compute_speeds_from_times(t_diffs: list, distances: list) -> list:
    res = []
    for i, d_diff in enumerate(distances):
        if i == 0:
            res.append(0)
        else:
            res.append(d_diff / t_diffs[i])
    return res


# 距離については累計を、speedについては区間ごとに評価すべき
def compute_fee(times: list, distances: list) -> int:
    base_cost = 0
    total_distance = sum(_process_midnight_section(times, distances))
    if total_distance <= 0:
        base_cost = 0
    elif total_distance <= INITIAL_BORDER:
        base_cost = INITIAL_COST
    else:
        additional_cost = ((total_distance - INITIAL_BORDER) //
                           ADDITIONAL_BORDER) * ADDITIONAL_COST_UNIT
        base_cost = INITIAL_COST + additional_cost

    low_speed_cost = 0
    t_diffs = _compute_time_diffs(times)
    speeds = _compute_speeds_from_times(t_diffs, distances)
    for s, t_diff in zip(speeds, t_diffs):
        if s <= LOW_SPEED_UPPER_LIMIT:
            low_speed_cost += (t_diff // LOW_SPEED_TIME_UNIT) * \
                LOW_SPEED_COST_UNIT

    return base_cost + low_speed_cost

# data reading


def read_data(path: str):
    times = []
    distances = []
    with open(path) as f:
        for l in f.readlines():
            t, d = l.split()
            times.append(t)
            distances.append(float(d))
    return times, distances


if __name__ == '__main__':
    path = 'sample.txt'
    times, distances = read_data(path)
    fee = compute_fee(times, distances)
    print('fee :', fee)
