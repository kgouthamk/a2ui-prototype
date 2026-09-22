import { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import Paper from "@mui/material/Paper";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import ReactMarkdown from "react-markdown";
import { enrich } from "../api/enrich";
import { Renderer } from "../a2ui/Renderer";
import type { EnrichResult } from "../a2ui/schema";

const SAMPLE = `# Deployment Guide

Steps: 1. build the image 2. push to registry 3. roll out.

Note: never deploy on Friday.

Specs: region us-west-2, replicas 3, port 8080.

Tags: infra, kubernetes, prod`;

export default function Chat() {
  const [input, setInput] = useState(SAMPLE);
  const [result, setResult] = useState<EnrichResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState(0);

  async function onSend() {
    setLoading(true);
    setError(null);
    try {
      setResult(await enrich(input));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box sx={{ display: "grid", gridTemplateColumns: { md: "1fr 1fr" }, gap: 2 }}>
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Markdown input
        </Typography>
        <TextField
          multiline
          minRows={14}
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <Button
          variant="contained"
          sx={{ mt: 1 }}
          onClick={onSend}
          disabled={loading}
        >
          {loading ? <CircularProgress size={22} /> : "Enrich"}
        </Button>
        {error && (
          <Typography color="error" sx={{ mt: 1 }}>
            {error}
          </Typography>
        )}
      </Box>

      <Box>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 1 }}>
          <Tab label="A2UI widgets" />
          <Tab label="Cleaned markdown" />
        </Tabs>
        {!result && (
          <Typography color="text.secondary">Output appears here.</Typography>
        )}
        {result && tab === 0 && <Renderer node={result.a2ui} />}
        {result && tab === 1 && (
          <Paper variant="outlined" sx={{ p: 2 }}>
            <ReactMarkdown>{result.markdown}</ReactMarkdown>
          </Paper>
        )}
      </Box>
    </Box>
  );
}
