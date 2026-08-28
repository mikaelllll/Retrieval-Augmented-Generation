import { CircleHelp } from 'lucide-react'

export function Tooltip({ text }: { text: string }) {
  return (
    <span className="tooltip" tabIndex={0} aria-label={text}>
      <CircleHelp size={15} />
      <span className="tooltip__content" role="tooltip">{text}</span>
    </span>
  )
}

