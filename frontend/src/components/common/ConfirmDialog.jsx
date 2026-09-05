// Reusable yes/no confirmation dialog, built on the existing Modal.
// Used anywhere an action is disruptive enough to double-check first
// (logging out, recording a payment) instead of firing immediately.
import Modal from './Modal.jsx'
import Button from './Button.jsx'

export default function ConfirmDialog({
  open,
  title = 'Are you sure?',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'primary',
  onConfirm,
  onCancel,
  busy = false,
}) {
  if (!open) return null

  return (
    <Modal open={open} onClose={busy ? () => {} : onCancel}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      {message && <p className="page-description">{message}</p>}
      <div className="form-actions">
        <Button type="button" variant={confirmVariant} onClick={onConfirm} disabled={busy}>
          {busy ? 'Please wait...' : confirmLabel}
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={busy}>
          {cancelLabel}
        </Button>
      </div>
    </Modal>
  )
}
