// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {html} from '//resources/lit/v3_0/lit.rollup.js';

import type {AimiumAppElement} from './app.js';

export function getHtml(this: AimiumAppElement) {
  return html`<!--_html_template_start_-->
<main>
  <header>
    <p class="eyebrow">Websites. Context. Repeatable work.</p>
    <h1>Aimium</h1>
    <p class="intro">A browser workspace for the web and AI.</p>
    <p id="build-stage">Development foundation</p>
  </header>

  <section class="current" aria-labelledby="current-heading">
    <h2 id="current-heading">The first building block is here</h2>
    <p>This page runs inside Chromium. It establishes the native entry point
      for Aimium on desktop.</p>
    <p>AI connections, website actions, saved workspaces and workflow execution
      are not available in this build. This page does not connect to AI
      providers or control websites.</p>
  </section>

  <section aria-labelledby="planned-heading">
    <h2 id="planned-heading">Planned for future milestones</h2>
    <div class="milestones">
      <article>
        <h3>Websites with context</h3>
        <p>Keep a normal browsing session beside its AI conversation and
          workspace context.</p>
      </article>
      <article>
        <h3>Your choice of AI</h3>
        <p>Connect providers with your own keys or use local models, then
          choose a connector for each workspace.</p>
      </article>
      <article>
        <h3>Actions on the page</h3>
        <p>Ask the assistant to work in the current website, with visible
          actions and control over permissions.</p>
      </article>
      <article>
        <h3>Reusable workflows</h3>
        <p>Build processes with nodes and connections, and run them manually
          or from time and event triggers.</p>
      </article>
    </div>
  </section>

  <footer>Desktop targets: Windows · Linux · macOS</footer>
</main>
<!--_html_template_end_-->`;
}
