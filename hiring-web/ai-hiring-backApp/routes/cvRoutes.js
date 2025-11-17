const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { authenticate } = require('../middleware/auth');
const cvController = require('../controllers/cvController');

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, '..', 'Uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for PDF uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    // Generate unique filename: userId_timestamp.pdf
    // req.user is available because authenticate middleware runs before multer
    const userId = req.user?.userId || 'unknown';
    const timestamp = Date.now();
    const ext = path.extname(file.originalname);
    cb(null, `${userId}_${timestamp}${ext}`);
  }
});

const fileFilter = (req, file, cb) => {
  // Only accept PDF files
  if (file.mimetype === 'application/pdf') {
    cb(null, true);
  } else {
    cb(new Error('Only PDF files are allowed'), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  }
});

// Error handling middleware for multer
const handleMulterError = (err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File size exceeds 5MB limit' });
    }
    return res.status(400).json({ error: err.message });
  }
  if (err) {
    return res.status(400).json({ error: err.message || 'File upload error' });
  }
  next();
};

// All CV routes require authentication
// Note: authenticate must run before multer so req.user is available in filename function
// Important: More specific routes must come BEFORE generic :cvId routes
router.get('/status', authenticate, cvController.getCVStatus);
router.post('/upload', authenticate, upload.single('cv'), handleMulterError, cvController.uploadCV);
router.get('/:cvId/download', authenticate, cvController.downloadCV);
router.get('/:cvId/file', authenticate, cvController.getCVFile);
router.get('/:cvId/improvements', authenticate, cvController.getCVImprovements);
router.get('/:cvId/messages', authenticate, cvController.getMessages);
router.post('/:cvId/messages', authenticate, cvController.addMessage);
router.get('/:cvId', authenticate, cvController.getCVById);
router.delete('/:cvId', authenticate, cvController.deleteCV);

module.exports = router;
