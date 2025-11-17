const User = require('../models/user');
const CV = require('../models/cv');
const mongoose = require('mongoose');
const path = require('path');
const fs = require('fs').promises;

// Helper to ensure userId is a valid ObjectId
const toObjectId = (id) => {
  if (mongoose.Types.ObjectId.isValid(id)) {
    return typeof id === 'string' ? new mongoose.Types.ObjectId(id) : id;
  }
  return id;
};

/**
 * GET /api/cv/status
 * Returns all uploaded CVs + user basic info
 */
exports.getCVStatus = async (req, res) => {
  try {
    const userId = toObjectId(req.user.userId);
    const user = await User.findById(userId).select('fullName email');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Get all CVs for this user
    // Note: MongoDB collection will be named "cvs" (lowercase, plural)
    const cvs = await CV.find({ userId }).sort({ createdAt: -1 });

    return res.json({
      hasCV: cvs.length > 0,
      uploadedCvs: cvs.map(cv => ({
        _id: cv._id,
        path: cv.path,
        name: cv.name,
        cvImprovements: cv.cvImprovements,
        messages: cv.messages,
        createdAt: cv.createdAt,
        updatedAt: cv.updatedAt
      })),
      user: {
        id: user._id,
        fullName: user.fullName,
        email: user.email,
      },
    });
  } catch (error) {
    console.error('Get CV status error:', error);
    return res.status(500).json({ error: 'Server error while fetching CV status' });
  }
};

/**
 * POST /api/cv/upload
 * Upload a new CV → Creates a new CV document
 */
exports.uploadCV = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const userId = toObjectId(req.user.userId);
    const user = await User.findById(userId);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Store file info
    const filePath = `/uploads/${req.file.filename}`;
    
    // Create new CV document
    const newCV = new CV({
      userId: userId,
      path: filePath,
      name: req.file.originalname,
      cvImprovements: null,
      messages: []
    });

    console.log('Creating CV with data:', {
      userId: userId,
      path: filePath,
      name: req.file.originalname
    });

    await newCV.save();
    
    console.log('✅ CV saved successfully!');
    console.log('   CV ID:', newCV._id);
    console.log('   Collection name: cvs (lowercase, plural)');
    console.log('   Database:', mongoose.connection.name);

    // Get total count
    const totalCvs = await CV.countDocuments({ userId });

    return res.json({
      message: 'CV uploaded successfully',
      uploadedCv: {
        _id: newCV._id,
        path: newCV.path,
        name: newCV.name,
        cvImprovements: newCV.cvImprovements,
        messages: newCV.messages
      },
      totalCvs: totalCvs
    });
  } catch (error) {
    console.error('Upload CV error:', error);
    console.error('Error details:', error.message);
    console.error('Stack trace:', error.stack);
    return res.status(500).json({ 
      error: 'Server error during CV upload',
      details: error.message 
    });
  }
};

/**
 * GET /api/cv/:cvId
 * Returns a specific CV by ID
 */
exports.getCVById = async (req, res) => {
  try {
    const { cvId } = req.params;
    const userId = req.user.userId;

    const cv = await CV.findOne({ _id: cvId, userId });

    if (!cv) {
      return res.status(404).json({ error: 'CV not found' });
    }

    return res.json({
      _id: cv._id,
      path: cv.path,
      name: cv.name,
      cvImprovements: cv.cvImprovements,
      messages: cv.messages,
      createdAt: cv.createdAt,
      updatedAt: cv.updatedAt
    });
  } catch (error) {
    console.error('Get CV by ID error:', error);
    return res.status(500).json({ error: 'Server error while fetching CV' });
  }
};

/**
 * GET /api/cv/:cvId/improvements
 * Returns improvements for a specific CV by ID
 */
exports.getCVImprovements = async (req, res) => {
  try {
    const { cvId } = req.params;
    const userId = req.user.userId;

    const cv = await CV.findOne({ _id: cvId, userId });

    if (!cv) {
      return res.status(404).json({ error: 'CV not found' });
    }

    return res.json({
      improvements: cv.cvImprovements || null,
      cvPath: cv.path,
      cvName: cv.name
    });
  } catch (error) {
    console.error('Get CV improvements error:', error);
    return res.status(500).json({ error: 'Server error while fetching improvements' });
  }
};

/**
 * POST /api/cv/:cvId/messages
 * Add a message to the CV conversation
 */
exports.addMessage = async (req, res) => {
  try {
    const { cvId } = req.params;
    const { role, content } = req.body;
    const userId = req.user.userId;

    if (!role || !content) {
      return res.status(400).json({ error: 'Role and content are required' });
    }

    if (!['user', 'assistant'].includes(role)) {
      return res.status(400).json({ error: 'Role must be either "user" or "assistant"' });
    }

    const cv = await CV.findOne({ _id: cvId, userId });

    if (!cv) {
      return res.status(404).json({ error: 'CV not found' });
    }

    // Add message to array
    cv.messages.push({
      role,
      content,
      timestamp: new Date()
    });

    await cv.save();

    const addedMessage = cv.messages[cv.messages.length - 1];

    return res.json({
      message: 'Message added successfully',
      addedMessage: addedMessage,
      totalMessages: cv.messages.length
    });
  } catch (error) {
    console.error('Add message error:', error);
    return res.status(500).json({ error: 'Server error while adding message' });
  }
};

/**
 * GET /api/cv/:cvId/messages
 * Get all messages for a CV
 */
exports.getMessages = async (req, res) => {
  try {
    const { cvId } = req.params;
    const userId = req.user.userId;

    const cv = await CV.findOne({ _id: cvId, userId }).select('messages');

    if (!cv) {
      return res.status(404).json({ error: 'CV not found' });
    }

    return res.json({
      messages: cv.messages,
      totalMessages: cv.messages.length
    });
  } catch (error) {
    console.error('Get messages error:', error);
    return res.status(500).json({ error: 'Server error while fetching messages' });
  }
};

/**
 * GET /api/cv/:cvId/download
 * Downloads/returns the actual CV file
 */
exports.downloadCV = async (req, res) => {
  try {
    const { cvId } = req.params;
    const userId = req.user.userId;

    const cv = await CV.findOne({ _id: cvId, userId });

    if (!cv) {
      return res.status(404).json({ error: 'CV not found' });
    }

    // Build the full file path
    const filePath = path.join(__dirname, '..', cv.path);

    // Check if file exists
    try {
      await fs.access(filePath);
    } catch (err) {
      return res.status(404).json({ error: 'CV file not found on server' });
    }

    // Send the file
    res.download(filePath, cv.name, (err) => {
      if (err) {
        console.error('Download error:', err);
        if (!res.headersSent) {
          res.status(500).json({ error: 'Error downloading file' });
        }
      }
    });
  } catch (error) {
    console.error('Download CV error:', error);
    return res.status(500).json({ error: 'Server error while downloading CV' });
  }
};

/**
 * GET /api/cv/:cvId/file
 * Returns the CV file as binary/raw file
 */
exports.getCVFile = async (req, res) => {
  try {
    const { cvId } = req.params;
    const userId = req.user.userId;

    console.log('📥 getCVFile request:');
    console.log('   cvId:', cvId);
    console.log('   userId:', userId);
    console.log('   req.user:', req.user);

    const cv = await CV.findOne({ _id: cvId, userId });

    if (!cv) {
      console.error('❌ CV not found. Query: _id=' + cvId + ', userId=' + userId);
      return res.status(404).json({ error: 'CV not found' });
    }

    console.log('✅ CV found:', cv.name, 'path:', cv.path);

    // Build the full file path
    const filePath = path.join(__dirname, '..', cv.path);
    console.log('   Full file path:', filePath);

    // Check if file exists
    try {
      await fs.access(filePath);
      console.log('✅ File exists');
    } catch (err) {
      console.error('❌ File not found at:', filePath);
      return res.status(404).json({ error: 'CV file not found on server' });
    }

    // Send the file with appropriate content-type
    res.sendFile(filePath, (err) => {
      if (err) {
        console.error('❌ Send file error:', err);
        if (!res.headersSent) {
          res.status(500).json({ error: 'Error retrieving file' });
        }
      } else {
        console.log('✅ File sent successfully');
      }
    });
  } catch (error) {
    console.error('❌ Get CV file error:', error);
    return res.status(500).json({ error: 'Server error while retrieving CV file' });
  }
};

/**
 * DELETE /api/cv/:cvId
 * Deletes a CV + removes file
 */
exports.deleteCV = async (req, res) => {
  try {
    const { cvId } = req.params;
    const userId = req.user.userId;

    const cv = await CV.findOne({ _id: cvId, userId });

    if (!cv) {
      return res.status(404).json({ error: 'CV not found' });
    }

    // Delete file from disk
    try {
      const fileToDelete = path.join(__dirname, '..', cv.path);
      await fs.unlink(fileToDelete);
    } catch (err) {
      console.warn('Could not delete CV file:', err);
    }

    // Delete CV document
    await CV.deleteOne({ _id: cvId, userId });

    // Get remaining count
    const totalCvs = await CV.countDocuments({ userId });

    return res.json({
      message: 'CV deleted successfully',
      totalCvs: totalCvs
    });
  } catch (error) {
    console.error('Delete CV error:', error);
    return res.status(500).json({ error: 'Server error while deleting CV' });
  }
};
