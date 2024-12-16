const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();

// Enable CORSdeactiv ate
app.use(cors());

// Serve static files from the distress_details folder
const distressDetailsPath = path.join(__dirname, '../distress_details'); // Adjust the path to distress_details
app.use('/distress_details', express.static(distressDetailsPath));

// Serve static files from the descriptions folder
const descriptionsPath = path.join(__dirname, '../descriptions'); // Adjust the path to descriptions
app.use('/descriptions', express.static(descriptionsPath));

// Start the server
const PORT = process.env.PORT || 4001;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

