'use client'
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

// Define a type for the judgement object
type Judgement = {
  summary: string;
  analysis: string;
  scores: Record<string, number>;
  final_verdict: string;
};

export default function Home() {
  const [projectData, setProjectData] = useState<{ fileName: string; advocate: string; critic: string; judgement: string; scores: Record<string, number>; }[]>([]);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortCriteria, setSortCriteria] = useState<'name' | 'score'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const filteredProjects = projectData.filter(project => {
    const projectName = project.fileName?.split('/').pop()?.split('.')[0] || 'Unknown Project';
    return projectName.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const calculateAverageScore = (scores: Record<string, number>) => {
    const scoreValues = Object.values(scores);
    const total = scoreValues.reduce((acc, score) => acc + score, 0);
    return (total / scoreValues.length).toFixed(2);
  };

  const sortProjects = (projects: typeof projectData) => {
    return [...projects].sort((a, b) => {
      if (sortCriteria === 'name') {
        const nameA = a.fileName.toLowerCase();
        const nameB = b.fileName.toLowerCase();
        if (nameA < nameB) return sortOrder === 'asc' ? -1 : 1;
        if (nameA > nameB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      } else if (sortCriteria === 'score') {
        const scoreA = parseFloat(calculateAverageScore(a.scores));
        const scoreB = parseFloat(calculateAverageScore(b.scores));
        return sortOrder === 'asc' ? scoreA - scoreB : scoreB - scoreA;
      }
      return 0;
    });
  };

  const sortedProjects = sortProjects(filteredProjects);

  const formatJudgement = (judgement: string) => {
    try {
      const judgementObj = JSON.parse(judgement);
      return (
        <div className="judgement-container">
          <p><strong>Summary:</strong> {judgementObj['summary']}</p>
          <p><strong>Analysis:</strong> {judgementObj['analysis']}</p>
          <p><strong>Final Verdict:</strong> {judgementObj['final_verdict']}</p>
        </div>
      );
    } catch (error) {
      return <p>{judgement}</p>;
    }
  };

  useEffect(() => {
    // Use dynamic import to load all JSON files
    const importAll = (r: { keys: () => string[]; (key: string): { advocate: string; critic: string; judgement: string; scores: Record<string, number>; }; }) => r.keys().map((key: string) => ({ ...r(key), fileName: key }));
    // @ts-ignore
    const context = require.context('../content/complete_project_review_data', false, /\.json$/);
    const data = importAll(context);
    setProjectData(data);
  }, []);

  const formatScores = (scores: Record<string, number>) => {
    return Object.entries(scores).map(([key, value]) => {
      return `${key}: ${value}\n`;
    }).join('');
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-center text-2xl font-bold mb-4">What did Claude think of your submission?</h1>
      <p className="text-center  font-bold mb-4">These are generated scores by Claude. They don't represent the actual scores of the judges, my personal views, or the actual quality of the project. They are just for fun!</p>
      <div className="flex justify-between mb-4">
        <input
          type="text"
          placeholder="Search by project name"
          value={searchQuery}
          onChange={handleSearchChange}
          className="p-2 border rounded"
        />
        <div className="flex items-center">
          <label className="mr-2">Sort by:</label>
          <select
            value={sortCriteria}
            onChange={(e) => setSortCriteria(e.target.value as 'name' | 'score')}
            className="p-2 border rounded"
          >
            <option value="name">Name</option>
            <option value="score">Score</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="ml-2 p-2 border rounded"
          >
            {sortOrder === 'asc' ? 'Asc' : 'Desc'}
          </button>
        </div>
      </div>
      <div className="card-container grid grid-cols-1 gap-4">
        {sortedProjects.map((project, index) => {
          const projectName = project.fileName?.split('/').pop()?.split('.')[0] || 'Unknown Project';
          const isExpanded = expandedIndex === index;
          const averageScore = calculateAverageScore(project.scores);
          return (
            <Card key={index} className="project-card p-4 border rounded-lg shadow-md relative">
              <div className="absolute top-2 right-2 text-sm font-bold">Avg Score: {averageScore}</div>
              <CardHeader>
                <CardTitle><a href={`https://devpost.com/software/${projectName}`}>{projectName}</a></CardTitle>
              </CardHeader>
              <CardContent>
                <a><strong>Advocate:</strong> {isExpanded ? project.advocate : `${project.advocate.substring(0, 100)}...`}</a>
                <p><strong>Critic:</strong> {isExpanded ? project.critic : `${project.critic.substring(0, 100)}...`}</p>
                <p><strong>Judgement:</strong> {isExpanded ? formatJudgement(project.judgement) : `${project.judgement.substring(0, 100)}...`}</p>
                <p><strong>Scores:</strong> {project.scores ? formatScores(project.scores) : 'No scores available'}</p>
                <br />
                <button onClick={() => toggleExpand(index)}>{isExpanded ? 'Show Less' : 'Read More'}</button>
              </CardContent>
            </Card>
          )
        })}
      </div>
      <style jsx>{`
        .project-card {
          transition: transform 0.2s, box-shadow 0.2s;
          padding: 16px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          background-color: #fff;
        }

        .project-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .card-container {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 16px;
        }

        .card-title a {
          color: #333;
          font-size: 1.25rem;
          font-weight: bold;
          text-decoration: none;
        }

        .card-title a:hover {
          color: #0070f3;
        }

        .judgement-container {
          margin-top: 8px;
          font-size: 0.875rem;
          color: #555;
        }

        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 16px;
        }

        .text-center {
          text-align: center;
        }

        .font-bold {
          font-weight: bold;
        }

        .mb-4 {
          margin-bottom: 16px;
        }

        .p-4 {
          padding: 16px;
        }

        .border {
          border: 1px solid #e0e0e0;
        }

        .rounded-lg {
          border-radius: 8px;
        }

        .shadow-md {
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .relative {
          position: relative;
        }

        .absolute {
          position: absolute;
        }

        .top-2 {
          top: 8px;
        }

        .right-2 {
          right: 8px;
        }

        .text-sm {
          font-size: 0.875rem;
        }

        .font-bold {
          font-weight: bold;
        }
      `}</style>
    </div>
  );
}
