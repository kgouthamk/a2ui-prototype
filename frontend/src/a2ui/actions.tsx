import { createContext, useContext } from "react";

/**
 * The action channel.
 *
 * Presentational widgets never touch this. Interactive ones read `values` and call
 * `setValue`/`dispatch`, which is why they must be real components rather than the
 * inline render functions in the registry — hooks called from a plain function
 * inside a loop would bind to the Renderer and break on the next tree shape.
 */
export interface A2UIActionCtx {
  /** Current form state, keyed by each widget's props.name. */
  values: Record<string, unknown>;
  setValue: (name: string, value: unknown) => void;
  /** Send an action id + the collected values to the agent. */
  dispatch: (action: string) => void;
  /** True while a round trip is in flight; interactive widgets disable themselves. */
  pending: boolean;
}

/** Inert default, so a tree rendered outside a provider degrades instead of throwing. */
const INERT: A2UIActionCtx = {
  values: {},
  setValue: () => {},
  dispatch: () => {},
  pending: false,
};

export const ActionContext = createContext<A2UIActionCtx>(INERT);
export const ActionProvider = ActionContext.Provider;

export function useA2UIAction(): A2UIActionCtx {
  return useContext(ActionContext);
}
