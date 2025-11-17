const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
  role: {
    type: String,
    enum: ['user', 'assistant'],
    required: true
  },
  content: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
}, { _id: true });

const cvSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    path: {
      type: String,
      required: true
    },
    name: {
      type: String,
      required: true
    },
    cvImprovements: {
      type: String,
      default: null
    },
    messages: {
      type: [messageSchema],
      default: []
    }
  },
  { timestamps: true }
);

// Index for faster queries
cvSchema.index({ userId: 1, createdAt: -1 });

module.exports = mongoose.model('CV', cvSchema);

