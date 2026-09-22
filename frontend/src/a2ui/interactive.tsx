import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import CircularProgress from "@mui/material/CircularProgress";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import { useA2UIAction } from "./actions";

/**
 * Interactive widgets. Each is a real component so it can use hooks.
 *
 * A control that cannot work renders a visible warning rather than drawing
 * something that looks live and silently does nothing — the failure mode this
 * project has already been bitten by once.
 */

function MissingName({ widget }: { widget: string }) {
  return (
    <Alert severity="warning" sx={{ my: 1 }}>
      <code>{widget}</code> has no <code>name</code>, so its value cannot be
      submitted.
    </Alert>
  );
}

export function A2UITextField(p: Record<string, any>) {
  const { values, setValue, pending } = useA2UIAction();
  if (!p.name) return <MissingName widget="TextField" />;
  return (
    <TextField
      fullWidth
      size="small"
      sx={{ my: 1 }}
      label={p.label ?? p.name}
      placeholder={p.placeholder}
      multiline={Boolean(p.multiline)}
      minRows={p.multiline ? 3 : undefined}
      disabled={pending}
      value={String(values[p.name] ?? "")}
      onChange={(e) => setValue(p.name, e.target.value)}
    />
  );
}

export function A2UISelect(p: Record<string, any>) {
  const { values, setValue, pending } = useA2UIAction();
  if (!p.name) return <MissingName widget="Select" />;
  const options: string[] = p.options ?? [];
  const labelId = `a2ui-select-${p.name}`;
  return (
    <FormControl fullWidth size="small" sx={{ my: 1 }} disabled={pending}>
      <InputLabel id={labelId}>{p.label ?? p.name}</InputLabel>
      <Select
        labelId={labelId}
        label={p.label ?? p.name}
        value={String(values[p.name] ?? "")}
        onChange={(e) => setValue(p.name, e.target.value)}
      >
        {options.map((o, i) => (
          <MenuItem key={i} value={o}>
            {o}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

export function A2UICheckbox(p: Record<string, any>) {
  const { values, setValue, pending } = useA2UIAction();
  if (!p.name) return <MissingName widget="Checkbox" />;
  return (
    <FormControlLabel
      sx={{ display: "block" }}
      control={
        <Checkbox
          disabled={pending}
          checked={Boolean(values[p.name])}
          onChange={(e) => setValue(p.name, e.target.checked)}
        />
      }
      label={p.label ?? p.name}
    />
  );
}

export function A2UISwitch(p: Record<string, any>) {
  const { values, setValue, pending } = useA2UIAction();
  if (!p.name) return <MissingName widget="Switch" />;
  return (
    <FormControlLabel
      sx={{ display: "block" }}
      control={
        <Switch
          disabled={pending}
          checked={Boolean(values[p.name])}
          onChange={(e) => setValue(p.name, e.target.checked)}
        />
      }
      label={p.label ?? p.name}
    />
  );
}

export function A2UIButton(p: Record<string, any> & { action?: string | null }) {
  const { dispatch, pending } = useA2UIAction();
  // Captured into a const so the guard below narrows inside the onClick closure.
  const action = p.action;
  // No action means nothing would happen on click. Say so instead of pretending.
  if (!action) {
    return (
      <Alert severity="warning" sx={{ my: 1 }}>
        Button <strong>{p.label ?? "(unlabelled)"}</strong> has no{" "}
        <code>action</code>, so it cannot do anything.
      </Alert>
    );
  }
  return (
    <Button
      variant={p.variant ?? "contained"}
      sx={{ my: 1 }}
      disabled={pending}
      onClick={() => dispatch(action)}
      startIcon={pending ? <CircularProgress size={16} color="inherit" /> : undefined}
    >
      {p.label ?? "Submit"}
    </Button>
  );
}
