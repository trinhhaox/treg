<script>
import { useDashboard } from '../state/context'
import BrandMark from './BrandMark.vue'
import LangSwitch from './LangSwitch.vue'
export default { components: { BrandMark, LangSwitch }, setup: useDashboard }
</script>

<template>
  <div class="lp">
    <header class="lp-nav">
      <a href="/" class="brand"><BrandMark/>treg</a>
      <nav class="lp-links" style="display:flex;align-items:center;gap:12px">
        <LangSwitch />
        <a href="/tutorial">{{t('nav.tutorial')}}</a>
        <button class="iconbtn" @click="toggleTheme" :aria-label="theme==='dark'?'Light theme':'Dark theme'">{{theme==='dark'?'◐':'◑'}}</button>
      </nav>
    </header>
    <main class="lp-hero" style="min-height:55vh">
      <template v-if="shareGate">
        <div class="lp-eyebrow">shared with you</div>
        <h1 class="lp-h1">{{shareGate.name}} <span style="color:var(--accent)">· {{shareGate.kind}}</span></h1>
        <p class="lp-lead">A teammate shared this {{shareGate.kind}} with you. Sign in to view it.</p>
      </template>
      <template v-else>
        <h1 class="lp-h1">{{t('auth.signin_title')}}</h1>
        <p class="lp-lead">{{t('auth.dialog_sub_default')}}</p>
      </template>
      <div class="lp-cta"><button class="btn primary lg" @click="demo.signin=true">{{shareGate?'Sign in to view':t('auth.signin_btn')}}</button></div>
    </main>
  </div>
</template>
