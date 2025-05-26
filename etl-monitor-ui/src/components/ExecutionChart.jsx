import React, { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip } from "recharts";
import axios from "axios";

const COLORS = ["#00C49F", "#FF8042"];

const ExecutionChart = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:8000/estadisticas").then((res) => {
      setStats([
        { name: "Éxitos", value: res.data.exitosas },
        { name: "Fallos", value: res.data.fallidas },
      ]);
    });
  }, []);

  return stats ? (
    <PieChart width={300} height={300}>
      <Pie
        data={stats}
        cx={150}
        cy={150}
        outerRadius={100}
        fill="#8884d8"
        dataKey="value"
        label
      >
        {stats.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index]} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  ) : (
    <p>Cargando estadísticas...</p>
  );
};

export default ExecutionChart;
