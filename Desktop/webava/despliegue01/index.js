require('dotenv').config();
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.send('¡Hola Mundo desde Node.js desplegado!');
});

app.listen(port, () => {
    console.log(`Servidor ejecutándose en puerto ${port}`);
});