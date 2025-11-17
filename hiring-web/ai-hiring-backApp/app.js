require('dotenv').config();
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const path = require('path');

const authRoutes = require('./routes/authRoutes');
const cvRoutes = require('./routes/cvRoutes');

const app = express();

// CORS
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:4200',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static(path.join(__dirname, 'Uploads')));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/cv', cvRoutes);

// MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/TaskForce')
  .then(() => {
    console.log('✅ MongoDB connecté');
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
      console.log(`🚀 Serveur en cours d'exécution sur le port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error('❌ Erreur MongoDB :', err);
    process.exit(1);
  });