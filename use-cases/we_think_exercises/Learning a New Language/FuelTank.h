#pragma once

class FuelTank {
public:
    FuelTank(float capacity_liters, float initial_liters);

    float capacity() const;
    float level() const;
    float percent_full() const;

    void add_fuel(float liters);
    float consume_fuel(float liters);

private:
    float capacity_liters_ = 0.0f;
    float level_liters_ = 0.0f;
};
