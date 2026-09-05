// TODO: shared button component (variants: primary/secondary/danger).
export default function Button({ children, ...props }) {
  return <button {...props}>{children}</button>
}
