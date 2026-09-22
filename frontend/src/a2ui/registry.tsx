import { Fragment, type ReactNode } from "react";
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
import {
  A2UIButton,
  A2UICheckbox,
  A2UISelect,
  A2UISwitch,
  A2UITextField,
} from "./interactive";

type P = Record<string, any>;

/**
 * The registry: type -> render function. This is where you control HOW a
 * widget looks. Add a widget = add one entry here (+ schema + prompt).
 */
export const registry: Record<
  WidgetType,
  (props: P, children: ReactNode, action?: string | null) => ReactNode
> = {
  Card: (_p, children) => (
    // containerType lets descendants query THIS card's width. Three cards across a
    // half-width panel are narrow even on a big screen, and a viewport media query
    // cannot see that.
    <Card variant="outlined" sx={{ mb: 2, containerType: "inline-size" }}>
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

  // MUI's h1-h3 are hero/display sizes — mapping a markdown level straight onto
  // them renders a `###` section title at ~3rem inside a card. Scale the visual
  // variant down by three steps while keeping the semantic tag accurate.
  Heading: (p) => {
    const level = Math.min(6, Math.max(1, p.level ?? 3));
    const variant = (["h4", "h5", "h6", "subtitle1", "subtitle2", "subtitle2"] as const)[
      level - 1
    ];
    return (
      <Typography
        variant={variant}
        component={`h${level}` as any}
        gutterBottom
        sx={{ fontWeight: 600 }}
      >
        {p.text}
      </Typography>
    );
  },

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

  // Lays its children out side by side — the thing that turns several Cards into a
  // stack of cards rather than a column of them. Collapses to one column on narrow
  // screens. Children arrive wrapped in a div by the Renderer, hence the `& > div`.
  Grid: (p, children) => {
    const cols = Math.min(4, Math.max(1, Number(p.columns) || 2));
    return (
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: `repeat(${cols}, minmax(0, 1fr))`,
          },
          gap: 2,
          mb: 2,
          // Cards carry their own bottom margin; inside a grid the gap governs.
          "& > div > *": { mb: 0, height: "100%" },
        }}
      >
        {children}
      </Box>
    );
  },

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

  // A definition list, not a stack of ListItems: the label reads as the label and
  // the value as the value. The previous version passed value as `primary` and key
  // as `secondary`, which rendered every fact upside down.
  KeyValueList: (p) => (
    <Box
      component="dl"
      sx={{
        display: "grid",
        gridTemplateColumns: { xs: "1fr", sm: "minmax(0, max-content) minmax(0, 1fr)" },
        columnGap: 2,
        rowGap: 1,
        my: 1,
        // Too narrow for two columns (e.g. inside a card in a 3-up Grid): stack the
        // label above its value instead of hyphenating both into unreadable strips.
        "@container (max-width: 300px)": {
          gridTemplateColumns: "1fr",
          rowGap: 0.25,
          "& dd": { mb: 1 },
        },
      }}
    >
      {(p.items ?? []).map((it: { key: string; value: string }, i: number) => (
        <Fragment key={i}>
          <Typography component="dt" variant="body2" color="text.secondary">
            {it.key}
          </Typography>
          <Typography
            component="dd"
            variant="body2"
            sx={{ m: 0, fontWeight: 500, overflowWrap: "break-word" }}
          >
            {it.value}
          </Typography>
        </Fragment>
      ))}
    </Box>
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

  // Interactive. These are real components, not inline render functions, so they
  // can use hooks to reach the action context (see actions.tsx).
  Button: (p, _children, action) => <A2UIButton {...p} action={action} />,
  TextField: (p) => <A2UITextField {...p} />,
  Select: (p) => <A2UISelect {...p} />,
  Checkbox: (p) => <A2UICheckbox {...p} />,
  Switch: (p) => <A2UISwitch {...p} />,
};
