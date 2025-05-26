import React, { useState } from "react";
import ExecutionTable from "../components/ExecutionTable";
import ExecutionChart from "../components/ExecutionChart";
import axios from "axios";

const Home = () => {
  const [detalle, setDetalle] = useState(null);

  const obtenerDetalle = (id) => {
    axios.get(`http://localhost:8000/ejecuciones/${id}`).then((res) => {
      setDetalle(res.data);
    });
  };

  return (
    <div>
      <h1>Monitor de Procesos ETL</h1>
      <ExecutionChart />
      <ExecutionTable onSelect={obtenerDetalle} />
      {detalle && (
        <div>
          <h2>Detalle de ejecución</h2>
          <pre>{JSON.stringify(detalle, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default Home;
