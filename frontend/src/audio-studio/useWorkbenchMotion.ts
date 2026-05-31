import { useEffect, useRef } from "react";

import gsap from "gsap";

export function useWorkbenchMotion(enabledKey: string | null) {
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!enabledKey || !rootRef.current) {
      return;
    }

    const root = rootRef.current;
    const motion = gsap.matchMedia();
    motion.add(
      {
        reduce: "(prefers-reduced-motion: reduce)",
        animate: "(prefers-reduced-motion: no-preference)"
      },
      (context) => {
        if (context.conditions?.reduce) {
          gsap.set(root.querySelectorAll(".a1-motion-item"), { autoAlpha: 1, clearProps: "transform" });
          return;
        }

        gsap.fromTo(
          root.querySelectorAll(".a1-motion-item"),
          { autoAlpha: 0, y: 10 },
          {
            autoAlpha: 1,
            y: 0,
            clearProps: "transform,visibility",
            duration: 0.34,
            ease: "power2.out",
            stagger: 0.045,
            overwrite: "auto"
          }
        );
      },
      root
    );

    return () => motion.revert();
  }, [enabledKey]);

  return rootRef;
}
