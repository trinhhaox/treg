<script>
import { useDashboard } from '../state/context'
import BrandMark from './BrandMark.vue'
import LangSwitch from './LangSwitch.vue'
export default { components: { BrandMark, LangSwitch }, setup: useDashboard }
</script>

<template>
<div class="pubnav" >
      <a class="brand" href="/"><BrandMark/>treg</a>
      <nav class="pubnav-links">
        <a href="/catalog" aria-current="page">{{t('nav.catalog')}}</a>
        <a href="/tutorial">{{t('nav.tutorial')}}</a>
        <a href="/docs">API</a>
        <LangSwitch />
        <a class="hidem" href="https://github.com/superdesigndev/treg" target="_blank" rel="noopener">GitHub ↗</a>
        <a @click="openSignin()">{{t('nav.signin')}}</a>
        <button class="btn primary sm" @click="openSignin()">{{t('nav.start_free')}}</button>
      </nav>
    </div>
</template>
