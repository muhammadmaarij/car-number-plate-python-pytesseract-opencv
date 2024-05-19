const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
const port = 5000;

// MongoDB connection
const uri =
  "mongodb+srv://a:a@cluster0.1cih6pg.mongodb.net/car-number?retryWrites=true&w=majority";
mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });

const connection = mongoose.connection;
connection.once("open", () => {
  console.log("MongoDB database connection established successfully");
});

app.use(cors());
app.use(bodyParser.json());

// LicensePlate Schema
const licensePlateSchema = new mongoose.Schema(
  {
    license_plate: String,
    timestamp: { type: Date, default: Date.now },
  },
  { collection: "number-plates" }
);

const LicensePlate = mongoose.model("LicensePlate", licensePlateSchema);

// Route
app.get("/license-plates", async (req, res) => {
  try {
    console.log("Fetching plates from database...");
    const plates = await LicensePlate.find();
    console.log("Retrieved plates:", plates);
    res.json(plates);
  } catch (err) {
    console.error("Error retrieving plates:", err);
    res.status(400).json("Error: " + err);
  }
});

app.listen(port, () => {
  console.log(`Server is running on port: ${port}`);
});
