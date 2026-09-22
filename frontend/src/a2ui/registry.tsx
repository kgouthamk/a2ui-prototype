import type { ReactNode } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Divider from "@mui/material/Divider";
import Box from "@mui/material/Box";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import StepContent from "@mui/material/StepContent";
import Stepper from "@mui/material/Stepper";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ReactMarkdown from "react-markdown";
import type { WidgetType } from "./schema";

type P = Record<string, any>;

/**
 * The registry: type -> render function. This is where you control HOW a
 * widget looks. Add a widget = add one entry here (+ schema + prompt).
 */
export const registry: Record<
  WidgetType,
  (props: P, children: ReactNode) => ReactNode
> = {
  Card: (_p, children) => (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>{children}</CardContent>
    </Card>
  ),

  Section: (p, children) => (
    <Box sx={{ mb: 2 }}>
      {p.title && (
        <Typography variant="h6" gutterBottom>
          {p.title}
        </Typography>
      )}
      {children}
    </Box>
  ),

  Heading: (p) => (
    <Typography variant={`h${Math.min(6, Math.max(1, p.level ?? 5))}` as any} gutterBottom>
      {p.text}
    </Typography>
  ),

  Text: (p) => (
    <Typography variant="body1" sx={{ mb: 1 }}>
      {p.text}
    </Typography>
  ),

  MarkdownBlock: (p) => (
    <Box sx={{ "& p": { mb: 1 } }}>
      <ReactMarkdown>{p.markdown ?? ""}</ReactMarkdown>
    </Box>
  ),

  Alert: (p) => (
    <Alert severity={p.severity ?? "info"} sx={{ mb: 1 }}>
      {p.text}
    </Alert>
  ),

  ChipGroup: (p) => (
    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 1 }}>
      {(p.chips ?? []).map((c: string, i: number) => (
        <Chip key={i} label={c} />
      ))}
    </Stack>
  ),

  Divider: () => <Divider sx={{ my: 2 }} />,

  Table: (p) => (
    <Table size="small" sx={{ mb: 1 }}>
      <TableHead>
        <TableRow>
          {(p.columns ?? []).map((c: string, i: number) => (
            <TableCell key={i}>
              <strong>{c}</strong>
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {(p.rows ?? []).map((row: string[], r: number) => (
          <TableRow key={r}>
            {row.map((cell, c) => (
              <TableCell key={c}>{cell}</TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),

  KeyValueList: (p) => (
    <List dense>
      {(p.items ?? []).map((it: { key: string; value: string }, i: number) => (
        <ListItem key={i} disableGutters>
          <ListItemText primary={it.value} secondary={it.key} />
        </ListItem>
      ))}
    </List>
  ),

  List: (p) => (
    <List dense sx={{ listStyleType: "disc", pl: 3 }}>
      {(p.items ?? []).map((it: string, i: number) => (
        <ListItem key={i} sx={{ display: "list-item" }} disableGutters>
          {it}
        </ListItem>
      ))}
    </List>
  ),

  Stepper: (p) => (
    <Stepper orientation="vertical" sx={{ mb: 1 }}>
      {(p.steps ?? []).map(
        (s: { label: string; detail?: string }, i: number) => (
          <Step key={i} active expanded>
            <StepLabel>{s.label}</StepLabel>
            {s.detail && <StepContent>{s.detail}</StepContent>}
          </Step>
        )
      )}
    </Stepper>
  ),

  Accordion: (p) => (
    <Box sx={{ mb: 1 }}>
      {(p.panels ?? []).map(
        (panel: { summary: string; detail: string }, i: number) => (
          <Accordion key={i}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              {panel.summary}
            </AccordionSummary>
            <AccordionDetails>{panel.detail}</AccordionDetails>
          </Accordion>
        )
      )}
    </Box>
  ),
};
