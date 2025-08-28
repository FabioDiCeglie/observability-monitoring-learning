const PORT = process.env.PORT || "8080";
const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("Hello World");
});

app.get("/date", (req, res) => {
    res.json({ date: new Date() });
  });

app.listen(parseInt(PORT, 10), () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});