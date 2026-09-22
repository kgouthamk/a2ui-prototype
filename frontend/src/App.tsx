import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Chat from "./components/Chat";

export default function App() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4">A2UI Prototype</Typography>
        <Typography color="text.secondary">
          Markdown in → cleaned markdown + Material Design widgets out.
        </Typography>
      </Box>
      <Chat />
    </Container>
  );
}
