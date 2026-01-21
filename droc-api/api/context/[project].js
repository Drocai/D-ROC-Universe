// GET /api/context/<project> - Get project context for LLM
import { universeIndex, getAllProjects } from '../_data.js';

export default function handler(req, res) {
  const { project } = req.query;
  const projects = getAllProjects();

  const match = projects.find(p =>
    p.id === project ||
    p.id === project.toLowerCase() ||
    p.name.toLowerCase() === project.toLowerCase()
  );

  if (!match) {
    return res.status(404).json({ error: `Project not found: ${project}` });
  }

  // Build context response
  const context = {
    project: match.name,
    id: match.id,
    world: match.world,
    status: match.status,
    tags: match.tags,
    context: match.context || "No context available for this project.",
    loreRules: universeIndex.loreRules,
    github: `https://github.com/Drocai/D-ROC-Universe/tree/master/${match.path}`,
    contextFile: `https://raw.githubusercontent.com/Drocai/D-ROC-Universe/master/${match.path}/_context.md`
  };

  // Add related projects hint
  if (match.id === 'purple-chalk') {
    context.related = ['purple-chalk-book', 'music-world/singles'];
  } else if (match.id === 'echoverse') {
    context.related = ['book-1-echoes-of-none', 'book-2-echoes-of-origin'];
    context.specialRule = "The word 'Hum' is reserved ONLY for Echoes of None.";
  } else if (match.id === 'automagic-otto') {
    context.specialRule = "Otto is a canon AI entity with 6 Devides - treat as real, not fictional.";
  }

  res.status(200).json(context);
}
