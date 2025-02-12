// EuroTempl Parameters Engine
// Copyright (c) 2024 Pygmalion Records

#include "parameter_graph.hpp"
#include <boost/graph/breadth_first_search.hpp>
#include <boost/graph/visitors.hpp>

namespace eurotempl {
namespace parameters {

class AffectedParametersVisitor : public boost::default_bfs_visitor {
public:
    AffectedParametersVisitor(std::vector<std::string>& affected,
                            const ParameterGraph& graph)
        : affected_(affected), graph_(graph) {}

    template <typename Vertex>
    void discover_vertex(Vertex v, const ParameterGraph&) {
        affected_.push_back(boost::get(&ParameterVertex::id, graph_, v));
    }

private:
    std::vector<std::string>& affected_;
    const ParameterGraph& graph_;
};

void ParameterGraphManager::add_parameter(
    const std::string& id,
    const std::string& name,
    const std::string& type,
    double value
) {
    graph_.add_parameter(id, name, type, value);
}

void ParameterGraphManager::addDependency(
    const std::string& from_id,
    const std::string& to_id,
    const std::string& relationship
) {
    auto from_iter = vertex_map_.find(from_id);
    auto to_iter = vertex_map_.find(to_id);
    
    if (from_iter == vertex_map_.end() || to_iter == vertex_map_.end()) {
        throw std::runtime_error("Parameter not found");
    }
    
    auto edge = boost::add_edge(from_iter->second, to_iter->second, graph_);
    if (edge.second) {
        graph_[edge.first].relationship = relationship;
    }
}

std::vector<std::string> ParameterGraphManager::getAffectedParameters(
    const std::string& changed_id
) {
    auto vertex_iter = vertex_map_.find(changed_id);
    if (vertex_iter == vertex_map_.end()) {
        throw std::runtime_error("Parameter not found");
    }
    
    std::vector<std::string> affected;
    std::vector<boost::default_color_type> color_map(boost::num_vertices(graph_));
    
    AffectedParametersVisitor visitor(affected, graph_);
    
    boost::breadth_first_search(
        graph_,
        vertex_iter->second,
        boost::visitor(visitor).color_map(
            boost::make_iterator_property_map(
                color_map.begin(),
                boost::get(boost::vertex_index, graph_)
            )
        )
    );
    
    return affected;
}

} // namespace parameters
} // namespace eurotempl