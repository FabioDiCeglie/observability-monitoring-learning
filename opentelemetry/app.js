require("./tracing");

const PORT = process.env.PORT || "8080";
const express = require("express");
const { countAllRequests } = require("./monitoring");
const app = express();
const axios = require("axios");

app.use(countAllRequests());

app.get("/", (req, res) => {
  axios
    .get(`http://localhost:${PORT}/middle-tier`)
    .then(() => axios.get(`http://localhost:${PORT}/middle-tier`))
    .then((result) => {
      res.send(result.data);
    })
    .catch((err) => {
      console.error(err);
      res.status(500).send("Error");
    });
});

app.get("/date", (req, res) => {
  res.json({ date: new Date() });
});

app.get("/backend", (req, res) => {
  res.json({ message: "Backend" });
});

app.get("/middle-tier", (req, res) => {
  axios
    .get(`http://localhost:${PORT}/backend`)
    .then(() => axios.get(`http://localhost:${PORT}/backend`))
    .then((result) => {
      res.send(result.data);
    })
    .catch((err) => {
      console.error(err);
      res.status(500).send("Error");
    });
});

app.listen(parseInt(PORT, 10), () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
