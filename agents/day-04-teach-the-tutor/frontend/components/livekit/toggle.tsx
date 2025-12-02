'use client';

import * as React from 'react';
import { type VariantProps, cva } from 'class-variance-authority';
import * as TogglePrimitive from '@radix-ui/react-toggle';
import { cn } from '@/lib/utils';

const toggleVariants = cva(
  [
    'inline-flex items-center justify-center gap-2 rounded-sm',
    'text-sm font-light whitespace-nowrap',
    'cursor-pointer outline-none transition-all duration-200',
    'hover:bg-foreground/5',
    'disabled:pointer-events-none disabled:opacity-40',
    'data-[state=on]:bg-foreground/10 data-[state=on]:text-foreground',
    'focus-visible:ring-ring/30 focus-visible:ring-1',
    'aria-invalid:ring-destructive/20 aria-invalid:border-destructive',
    "[&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 [&_svg]:shrink-0",
  ],
  {
    variants: {
      variant: {
        default: 'bg-transparent border border-foreground/10',
        primary:
          'bg-foreground/5 border border-foreground/10 data-[state=on]:bg-foreground/10 hover:bg-foreground/10',
        secondary:
          'bg-foreground/5 border border-foreground/10 data-[state=on]:bg-foreground/15 hover:bg-foreground/10',
        outline:
          'border border-foreground/10 bg-transparent hover:bg-foreground/5',
      },
      size: {
        default: 'h-9 px-4 py-2 has-[>svg]:px-3',
        sm: 'h-8 gap-1.5 px-3 has-[>svg]:px-2.5',
        lg: 'h-10 px-6 has-[>svg]:px-4',
        icon: 'size-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

function Toggle({
  className,
  variant,
  size,
  ...props
}: React.ComponentProps<typeof TogglePrimitive.Root> & VariantProps<typeof toggleVariants>) {
  return (
    <TogglePrimitive.Root
      data-slot="toggle"
      className={cn(toggleVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Toggle, toggleVariants };
