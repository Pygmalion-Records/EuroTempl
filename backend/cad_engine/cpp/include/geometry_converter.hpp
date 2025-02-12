// EuroTempl System
// Copyright (c) 2024 Pygmalion Records

#pragma once

#include <vector>
#include <array>
#include <memory>

namespace eurotempl {

class GeometryConverter {
public:
    // Convert coordinates to grid-aligned points
    static std::vector<std::array<double, 3>> alignToGrid(
        const std::vector<std::array<double, 3>>& points,
        double gridSize = 25.0) noexcept;

    // Validate grid alignment
    static bool validateGridAlignment(
        const std::vector<std::array<double, 3>>& points,
        double gridSize = 25.0) noexcept;

    // Convert between coordinate systems
    static std::vector<std::array<double, 3>> toGeos(
        const std::vector<std::array<double, 3>>& points) noexcept;
    
    static std::vector<std::array<double, 3>> fromGeos(
        const std::vector<std::array<double, 3>>& points) noexcept;

private:
    static constexpr double EPSILON = 1e-6;
    static double roundToGrid(double value, double gridSize) noexcept;
};

} // namespace eurotempl