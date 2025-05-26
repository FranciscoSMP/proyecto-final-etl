import React, { useEffect, useState } from "react";
import axios from "axios";

const ExecutionTable = ({ onSelect }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/ejecuciones").then((res) => {
      setData(res.data);
    });
  }, []);

  return (
    <table>
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Duración (s)</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        {data.map((ejecucion) => (
          <tr key={ejecucion._id} onClick={() => onSelect(ejecucion._id)}>
            <td>{new Date(ejecucion.fecha_ejecucion).toLocaleString()}</td>
            <td>{ejecucion.duracion.toFixed(2)}</td>
            <td>{ejecucion.estado}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ExecutionTable;
