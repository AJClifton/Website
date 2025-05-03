import Image from "next/image";
import TypeEffect from "./Components/TypeEffect"
import Cursor from "./Components/Cursor";

import type { Metadata } from 'next'
 
export const metadata: Metadata = {
  title: 'AJClifton',
  description: 'Main page for AJClifton.co.uk, a website owned by Alex Clifton.',
}

export default function Home() {
  return (
    <div className="bg-zinc-100 dark:bg-zinc-800 grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <h1 className="text-grey-500 dark:text-white text-3xl font-bold tracking-wider text-center content-stretch">AJClifton</h1>
        <p className="text-grey-500 dark:text-white text-base">I am working on this website very slowly.</p>
      </main>

      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center text-grey-500 dark:text-white">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://github.com/AJClifton"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image className="dark:invert"
            aria-hidden
            src="/github-mark.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Github (AJClifton)
        </a>

        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://github.com/horrid57"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image className="dark:invert"
            aria-hidden
            src="/github-mark.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Github (horrid57)
        </a>

        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://www.linkedin.com/in/alex-clifton-1a6102160/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image className="dark:invert"
            aria-hidden
            src="/inBug-Black.png"
            alt="Window icon"
            width={16}
            height={16}
          />
          LinkedIn
        </a>
      </footer>
    </div>
  );
}
