// EuroTempl Parameters Engine
// Copyright (c) 2024 Pygmalion Records

#pragma once

#include <boost/graph/adjacency_list.hpp>
#include <string>
#include <memory>

namespace eurotempl {
namespace parameters {

struct ParameterVertex {
    std::string id;
    std::string name;
    std::string type;
    double value;
};

struct ParameterEdge {
    std::string relationship;
};

using ParameterGraph = boost::adjacency_list<
    boost::vecS,
    boost::vecS,
    boost::bidirectionalS,
    ParameterVertex,
    ParameterEdge
>;

class ParameterGraphManager {
public:
    ParameterGraphManager() = default;
    
    void addParameter(const std::string& id, const std::string& name,
                     const std::string& type, double value);
    
    void addDependency(const std::string& from_id, const std::string& to_id,
                      const std::string& relationship);
    
    std::vector<std::string> getAffectedParameters(const std::string& changed_id);

private:
    ParameterGraph graph_;
    std::unordered_map<std::string, size_t> vertex_map_;
};

} // namespace parameters
} // namespace eurotempl