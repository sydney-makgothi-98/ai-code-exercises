#include "FuelTank.h"

#include <algorithm>

FuelTank::FuelTank(float capacity_liters, float initial_liters)
    : capacity_liters_(capacity_liters),
      level_liters_(std::clamp(initial_liters, 0.0f, capacity_liters))
{
}

float FuelTank::capacity() const
{
    return capacity_liters_;
}

float FuelTank::level() const
{
    return level_liters_;
}

float FuelTank::percent_full() const
{
    if (capacity_liters_ <= 0.0f) {
        return 0.0f;
    }

    return (level_liters_ / capacity_liters_) * 100.0f;
}

void FuelTank::add_fuel(float liters)
{
    level_liters_ = std::min(capacity_liters_, level_liters_ + liters);
}

float FuelTank::consume_fuel(float liters)
{
    float consumed = std::min(level_liters_, liters);
    level_liters_ -= consumed;
    return consumed;
}
