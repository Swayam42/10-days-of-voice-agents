import * as React from 'react';
import { type VariantProps, cva } from 'class-variance-authority';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  [
    'text-xs font-light tracking-wide uppercase whitespace-nowrap',
    'inline-flex items-center justify-center gap-2 shrink-0 rounded-sm cursor-pointer outline-none transition-all duration-200',
    'focus-visible:ring-ring/30 focus-visible:ring-1',
    'disabled:pointer-events-none disabled:opacity-40',
    'aria-invalid:ring-destructive/20 aria-invalid:border-destructive',
    "[&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 [&_svg]:shrink-0",
  ],
  {
    variants: {
      variant: {
        default: 'bg-foreground/5 text-foreground border border-foreground/5 hover:bg-foreground/10',
        destructive: [
          'bg-foreground/10 text-foreground border border-foreground/10',
          'hover:bg-foreground/15',
        ],
        outline: [
          'border border-foreground/10 bg-background',
          'hover:bg-foreground/5',
        ],
        primary: 'bg-foreground text-background border border-foreground/10 hover:bg-foreground/90',
        secondary: 'bg-foreground/5 text-foreground border border-foreground/5 hover:bg-foreground/10',
        ghost: 'hover:bg-foreground/5',
        link: 'text-foreground underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2 has-[>svg]:px-3',
        sm: 'h-8 gap-1.5 px-3 has-[>svg]:px-2.5',
        lg: 'h-11 px-6 has-[>svg]:px-4',
        icon: 'size-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
