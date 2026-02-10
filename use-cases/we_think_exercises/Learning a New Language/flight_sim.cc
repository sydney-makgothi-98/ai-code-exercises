#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <tuple>
#include <vector>

namespace glm {
struct vec3 {
    float x = 0.0f;
    float y = 0.0f;
    float z = 0.0f;

    vec3() = default;
    vec3(float x_value, float y_value, float z_value) : x(x_value), y(y_value), z(z_value) {}

    vec3& operator+=(const vec3& other)
    {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }
};

inline vec3 operator+(const vec3& left, const vec3& right)
{
    return { left.x + right.x, left.y + right.y, left.z + right.z };
}

inline vec3 operator-(const vec3& left, const vec3& right)
{
    return { left.x - right.x, left.y - right.y, left.z - right.z };
}

inline vec3 operator-(const vec3& value)
{
    return { -value.x, -value.y, -value.z };
}

inline vec3 operator*(const vec3& value, float scalar)
{
    return { value.x * scalar, value.y * scalar, value.z * scalar };
}

inline vec3 operator*(float scalar, const vec3& value)
{
    return value * scalar;
}

inline vec3 operator/(const vec3& value, float scalar)
{
    return { value.x / scalar, value.y / scalar, value.z / scalar };
}

inline float dot(const vec3& left, const vec3& right)
{
    return left.x * right.x + left.y * right.y + left.z * right.z;
}

inline vec3 cross(const vec3& left, const vec3& right)
{
    return {
        left.y * right.z - left.z * right.y,
        left.z * right.x - left.x * right.z,
        left.x * right.y - left.y * right.x
    };
}

inline float length(const vec3& value)
{
    return std::sqrt(dot(value, value));
}

inline vec3 normalize(const vec3& value)
{
    float len = length(value);
    if (len <= 0.0f) {
        return {};
    }
    return value / len;
}

struct quat {
    float w = 1.0f;
    float x = 0.0f;
    float y = 0.0f;
    float z = 0.0f;

    quat() = default;
    quat(float w_value, float x_value, float y_value, float z_value)
        : w(w_value), x(x_value), y(y_value), z(z_value)
    {
    }

    quat(float w_value, const vec3& v) : w(w_value), x(v.x), y(v.y), z(v.z) {}
};

inline quat operator*(const quat& left, const quat& right)
{
    return {
        left.w * right.w - left.x * right.x - left.y * right.y - left.z * right.z,
        left.w * right.x + left.x * right.w + left.y * right.z - left.z * right.y,
        left.w * right.y - left.x * right.z + left.y * right.w + left.z * right.x,
        left.w * right.z + left.x * right.y - left.y * right.x + left.z * right.w
    };
}

inline vec3 operator*(const quat& q, const vec3& v)
{
    quat vq(0.0f, v);
    quat inv = { q.w, -q.x, -q.y, -q.z };
    quat rotated = q * vq * inv;
    return { rotated.x, rotated.y, rotated.z };
}

inline quat operator+(const quat& left, const quat& right)
{
    return { left.w + right.w, left.x + right.x, left.y + right.y, left.z + right.z };
}

inline quat operator*(const quat& q, float scalar)
{
    return { q.w * scalar, q.x * scalar, q.y * scalar, q.z * scalar };
}

inline quat normalize(const quat& q)
{
    float len = std::sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (len <= 0.0f) {
        return {};
    }
    return { q.w / len, q.x / len, q.y / len, q.z / len };
}

inline quat inverse(const quat& q)
{
    return { q.w, -q.x, -q.y, -q.z };
}

inline float degrees(float radians)
{
    return radians * (180.0f / 3.14159265358979323846f);
}

inline float clamp(float value, float min_value, float max_value)
{
    return std::max(min_value, std::min(value, max_value));
}

struct mat3 {
    float m[3][3] = {
        { 1.0f, 0.0f, 0.0f },
        { 0.0f, 1.0f, 0.0f },
        { 0.0f, 0.0f, 1.0f }
    };

    mat3() = default;

    mat3(std::initializer_list<float> values)
    {
        auto it = values.begin();
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 3; ++col) {
                if (it != values.end()) {
                    m[row][col] = *it++;
                }
            }
        }
    }
};

inline vec3 operator*(const mat3& mat, const vec3& v)
{
    return {
        mat.m[0][0] * v.x + mat.m[0][1] * v.y + mat.m[0][2] * v.z,
        mat.m[1][0] * v.x + mat.m[1][1] * v.y + mat.m[1][2] * v.z,
        mat.m[2][0] * v.x + mat.m[2][1] * v.y + mat.m[2][2] * v.z
    };
}
}

namespace phi {
using Seconds = float;
constexpr float PI = 3.14159265358979323846f;
constexpr glm::vec3 FORWARD = { 1.0f, 0.0f, 0.0f };
constexpr glm::vec3 RIGHT = { 0.0f, 0.0f, 1.0f };

inline float sq(float value)
{
    return value * value;
}

namespace units {
inline float meter_per_second(float value)
{
    return value;
}
}

class RigidBody {
private:
    glm::vec3 m_force{};  // world space
    glm::vec3 m_torque{}; // body space

public:
    virtual ~RigidBody() = default;

    float mass = 1.0f;                          // kg
    glm::vec3 position{};                       // world space
    glm::quat orientation{};                    // world space
    glm::vec3 velocity{};                       // world space, meter/second
    glm::vec3 angular_velocity{};               // body space, radians/second
    glm::mat3 inertia{}, inverse_inertia{};     // inertia tensor, body space
    bool apply_gravity = true;

    glm::vec3 transform_direction(const glm::vec3& direction) const
    {
        return orientation * direction;
    }

    glm::vec3 inverse_transform_direction(const glm::vec3& direction) const
    {
        return glm::inverse(orientation) * direction;
    }

    glm::vec3 get_point_velocity(const glm::vec3& point) const
    {
        return inverse_transform_direction(velocity) + glm::cross(angular_velocity, point);
    }

    void add_force_at_point(const glm::vec3& force, const glm::vec3& point)
    {
        m_force += transform_direction(force);
        m_torque += glm::cross(point, force);
    }

    void add_relative_force(const glm::vec3& force)
    {
        m_force += transform_direction(force);
    }

    virtual void update(float dt)
    {
        glm::vec3 acceleration = m_force / mass;
        if (apply_gravity) {
            acceleration.y -= 9.81f;
        }
        velocity += acceleration * dt;
        position += velocity * dt;

        angular_velocity += inverse_inertia *
            (m_torque - glm::cross(angular_velocity, inertia * angular_velocity)) * dt;
        orientation = orientation + (orientation * glm::quat(0.0f, angular_velocity)) * (0.5f * dt);
        orientation = glm::normalize(orientation);

        m_force = {};
        m_torque = {};
    }
};
}

namespace isa {
inline float get_air_density(float altitude_meters)
{
    float sea_level_density = 1.225f;
    float density = sea_level_density * std::exp(-altitude_meters / 8500.0f);
    return std::max(0.0f, density);
}
}

inline float scale(float value, float in_min, float in_max, float out_min, float out_max)
{
    if (in_max <= in_min) {
        return out_min;
    }
    float t = (value - in_min) / (in_max - in_min);
    return out_min + t * (out_max - out_min);
}

struct Airfoil {
    const float min_alpha;
    const float max_alpha;
    std::vector<glm::vec3> data;
    float cl_max = 1.2f;

    Airfoil(const std::vector<glm::vec3>& curve)
        : min_alpha(curve.front().x),
          max_alpha(curve.back().x),
          data(curve)
    {
    }

    std::tuple<float, float> sample(float alpha) const
    {
        float index = scale(alpha, min_alpha, max_alpha, 0.0f,
                            static_cast<float>(data.size() - 1));
        int i = static_cast<int>(glm::clamp(index, 0.0f, static_cast<float>(data.size() - 1)));
        return { data[i].y, data[i].z };
    }
};

struct Wing {
    const Airfoil* airfoil = nullptr;
    glm::vec3 center_of_pressure{};
    float area = 0.0f;
    float chord = 0.0f;
    float wingspan = 0.0f;
    glm::vec3 normal = { 0.0f, 1.0f, 0.0f };
    float aspect_ratio = 1.0f;
    float flap_ratio = 0.25f;
    float efficiency_factor = 0.9f;
    float control_input = 0.0f;

    Wing(const glm::vec3& position, float span, float chord_length, const Airfoil* airfoil_value,
         const glm::vec3& normal_value = { 0.0f, 1.0f, 0.0f }, float flap_ratio_value = 0.25f)
        : airfoil(airfoil_value),
          center_of_pressure(position),
          area(span * chord_length),
          chord(chord_length),
          wingspan(span),
          normal(normal_value),
          aspect_ratio(phi::sq(span) / area),
          flap_ratio(flap_ratio_value)
    {
    }

    void set_control_input(float input)
    {
        control_input = glm::clamp(input, -1.0f, 1.0f);
    }

    void apply_force(phi::RigidBody* rigid_body, phi::Seconds)
    {
        if (!airfoil) {
            return;
        }

        glm::vec3 local_velocity = rigid_body->get_point_velocity(center_of_pressure);
        float speed = glm::length(local_velocity);

        if (speed <= 1.0f) {
            return;
        }

        glm::vec3 drag_direction = glm::normalize(-local_velocity);
        glm::vec3 lift_direction = glm::normalize(glm::cross(glm::cross(drag_direction, normal), drag_direction));

        float angle_of_attack = glm::degrees(std::asin(glm::dot(drag_direction, normal)));
        auto [lift_coeff, drag_coeff] = airfoil->sample(angle_of_attack);

        if (flap_ratio > 0.0f) {
            float delta_lift_coeff = std::sqrt(flap_ratio) * airfoil->cl_max * control_input;
            lift_coeff += delta_lift_coeff;
        }

        float induced_drag_coeff = phi::sq(lift_coeff) / (phi::PI * aspect_ratio * efficiency_factor);
        drag_coeff += induced_drag_coeff;

        float air_density = isa::get_air_density(rigid_body->position.y);
        float dynamic_pressure = 0.5f * phi::sq(speed) * air_density * area;

        glm::vec3 lift = lift_direction * lift_coeff * dynamic_pressure;
        glm::vec3 drag = drag_direction * drag_coeff * dynamic_pressure;

        rigid_body->add_force_at_point(lift + drag, center_of_pressure);
    }
};

struct Engine {
    float throttle = 1.0f;
    float thrust = 0.0f;

    explicit Engine(float thrust_value) : thrust(thrust_value) {}

    void apply_force(phi::RigidBody* rigid_body) const
    {
        rigid_body->add_relative_force(phi::FORWARD * (throttle * thrust));
    }
};

struct Airplane : public phi::RigidBody {
    Engine engine;
    std::vector<Wing> elements;

    Airplane(float mass_value, float thrust_value, const glm::mat3& inertia_value, std::vector<Wing> wings)
        : engine(thrust_value),
          elements(std::move(wings))
    {
        mass = mass_value;
        inertia = inertia_value;
        inverse_inertia = inertia_value;
    }

    void update(float dt) override
    {
        engine.apply_force(this);
        for (auto& wing : elements) {
            wing.apply_force(this, dt);
        }
        phi::RigidBody::update(dt);
    }
};

static const std::vector<glm::vec3> NACA_0012_data = {
    { -10.0f, -0.6f, 0.08f },
    { 0.0f, 0.0f, 0.02f },
    { 10.0f, 0.6f, 0.08f }
};

static const std::vector<glm::vec3> NACA_2412_data = {
    { -10.0f, -0.5f, 0.07f },
    { 0.0f, 0.1f, 0.025f },
    { 10.0f, 0.8f, 0.09f }
};

int main()
{
    const float mass = 10000.0f;
    const float thrust = 50000.0f;

    const float wing_offset = -1.0f;
    const float tail_offset = -6.6f;

    const Airfoil NACA_0012(NACA_0012_data);
    const Airfoil NACA_2412(NACA_2412_data);

    std::vector<Wing> wings = {
        Wing({ wing_offset, 0.0f, -2.7f }, 6.96f, 2.50f, &NACA_2412),
        Wing({ wing_offset - 1.5f, 0.0f, -2.0f }, 3.80f, 1.26f, &NACA_0012),
        Wing({ wing_offset - 1.5f, 0.0f, 2.0f }, 3.80f, 1.26f, &NACA_0012),
        Wing({ wing_offset, 0.0f, 2.7f }, 6.96f, 2.50f, &NACA_2412),
        Wing({ tail_offset, -0.1f, 0.0f }, 6.54f, 2.70f, &NACA_0012),
        Wing({ tail_offset, 0.0f, 0.0f }, 5.31f, 3.10f, &NACA_0012, phi::RIGHT)
    };

    glm::mat3 inertia = {
        48531.0f, -1320.0f, 0.0f,
        -1320.0f, 256608.0f, 0.0f,
        0.0f, 0.0f, 211333.0f
    };

    Airplane airplane(mass, thrust, inertia, std::move(wings));
    airplane.position = { 0.0f, 2000.0f, 0.0f };
    airplane.velocity = { phi::units::meter_per_second(600.0f), 0.0f, 0.0f };

    for (int i = 0; i < 5; ++i) {
        airplane.update(0.016f);
        std::cout << "Step " << i << ": altitude=" << airplane.position.y << " m\n";
    }

    return 0;
}