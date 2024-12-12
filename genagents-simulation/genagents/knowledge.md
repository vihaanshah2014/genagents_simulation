# GenAgents Core Module Knowledge

## Purpose
Core functionality for creating and interacting with generative agents.

## Key Components
- `genagents.py`: Main agent class implementation
- `modules/`: Specialized functionality
  - `interaction.py`: Agent response generation
  - `memory_stream.py`: Memory management and reflection

## Agent Architecture
- Agents maintain a memory stream of observations and reflections
- Each memory has importance score and embedding
- Responses generated using context from relevant memories
- Support for categorical, numerical, and open-ended responses

## Best Practices
- Preserve memory stream structure when adding new features
- Maintain backward compatibility for agent save/load
- Keep agent state immutable during interactions
