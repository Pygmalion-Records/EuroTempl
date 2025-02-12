// EuroTempl System
// Copyright (c) 2024 Pygmalion Records

#include "geometry_converter.hpp"
#include <cmath>

namespace eurotempl {

double GeometryConverter::roundToGrid(double value, double gridSize) noexcept {
    return std::round(value / gridSize) * gridSize;
}

std::vector<std::array<double, 3>> GeometryConverter::alignToGrid(
    const std::vector<std::array<double, 3>>& points,
    double gridSize) noexcept {
    
    std::vector<std::array<double, 3>> aligned;
    aligned.reserve(points.size());

    for (const auto& point : points) {
        aligned.push_back({
            roundToGrid(point[0], gridSize),
            roundToGrid(point[1], gridSize),
            point[2]  // Z coordinate not grid-aligned as per requirements
        });
    }

    return aligned;
}

bool GeometryConverter::validateGridAlignment(
    const std::vector<std::array<double, 3>>& points,
    double gridSize) noexcept {
    
    for (const auto& point : points) {
        double xRemainder = std::fmod(point[0], gridSize);
        double yRemainder = std::fmod(point[1], gridSize);
        
        if (std::abs(xRemainder) > EPSILON || std::abs(yRemainder) > EPSILON) {
            return false;
        }
    }
    return true;
}

std::vector<std::array<double, 3>> GeometryConverter::toGeos(
    const std::vector<std::array<double, 3>>& points) noexcept {
    // GEOS uses the same coordinate system, just ensure grid alignment
    return alignToGrid(points);
}

std::vector<std::array<double, 3>> GeometryConverter::fromGeos(
    const std::vector<std::array<double, 3>>& points) noexcept {
    // GEOS uses the same coordinate system, just ensure grid alignment
    return alignToGrid(points);
}

} // namespace eurotempl