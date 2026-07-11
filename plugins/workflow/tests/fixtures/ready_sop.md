# Demo SOP

Status: Ready

## Summary

Run a deterministic demo workflow.

## Trigger

The operator requests the demo.

## Preconditions

The repository is available.

## Working Directory

Use the repository root.

## Inputs

No external inputs.

## Execution Harness

Run locally and serially.

## Allowed Actions

Read files and run validation.

## Forbidden Actions

Do not publish changes.

## Steps

Run the demo command.

## Validation

Require a zero exit code.

## Output Contract

Report the command and result.

## Stop Conditions

Stop on a failed required validation.

## Update Rules

Update this SOP when the command changes.

## Reuse Prompt

Execute this SOP exactly.

## Documented placeholder example

```text placeholder-example
Template syntax uses <sop-path> here.
```
