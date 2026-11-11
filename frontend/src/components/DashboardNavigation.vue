<script>
import { useDashboard } from '../state/context'
import BrandMark from './BrandMark.vue'
import Avatar from './ui/Avatar.vue'
import LangSwitch from './LangSwitch.vue'
export default {
  components: { BrandMark, Avatar, LangSwitch }, setup: useDashboard,
  data: () => ({ meAvatarBroken: false }),
  watch: { meAvatar() { this.meAvatarBroken = false } },
}
</script>

<template>
<header class="rd-top" >
      <div class="rd-identity">
        <a class="rd-brand brand" href="/" aria-label="treg home"><BrandMark/>treg</a>
        <div class="orgblock" v-if="authed">
          <div class="orgmain" :ref="el => setElement('orgmain', el)" @click="toggleOrgMenu" role="button" tabindex="0" @keydown.enter="toggleOrgMenu" @keydown.space.prevent="toggleOrgMenu" aria-haspopup="true" :aria-expanded="orgMenu" aria-label="Teams">
            <span class="role" :class="activeRole">{{activeRole}}</span>
            <Avatar v-if="activeOrg && activeOrg.avatar_url" :src="activeOrg.avatar_url" :name="activeName" :size="20" />
            <b class="orgname">{{activeName}}</b>
            <span class="orgcaret">▾</span>
          </div>
          <div class="dropdown" v-if="orgMenu" :style="orgMenuStyle" @click.stop>
            <div class="grp" style="margin:4px 10px 6px">{{t('common.your_teams')}}</div>
            <div class="orgrow" v-for="o in myOrgs" :key="o.slug" :class="{off:!connected(o.slug)}">
              <Avatar :src="o.avatar_url" :name="o.name||o.slug" :size="26" />
              <div class="orgrow-main">
                <div class="orgrow-name">{{o.name}}</div>
                <div class="orgrow-meta"><span class="role" :class="o.role">{{o.role}}</span><span v-if="isPersonal(o)" class="chip">{{t('common.personal')}}</span><span v-if="o.demo" class="chip demo">demo</span></div>
              </div>
              <button class="orgrow-btn" @click.stop="orgSettings(o)" :title="t('common.settings')" :aria-label="t('common.settings')">⚙</button>
              <span v-if="o.slug===activeSlugNow" class="orgrow-active">✓ {{t('common.active')}}</span>
              <button v-else-if="sessionMode || connected(o.slug)" class="orgrow-btn" @click.stop="switchTo(o)">{{t('common.switch')}}</button>
              <button v-else class="orgrow-btn" @click.stop="addOrg=true; orgMenu=false">{{t('common.token')}}</button>
            </div>
            <div class="orgrow-sep"></div>
            <button type="button" class="row" v-if="sessionMode" @click="newOrg=true; newOrgName=''; orgMenu=false"><span>{{t('common.new_team')}}</span></button>
            <button type="button" class="row" v-if="sessionMode" @click="showJoin=true; joinCode=''; joinErr=''; orgMenu=false"><span>{{t('common.join_code')}}</span></button>
            <button type="button" class="row" v-if="!sessionMode" @click="addOrg=true; orgMenu=false"><span>{{t('common.new_team')}}</span></button>
          </div>
        </div>


      </div>
      <nav class="rd-navs" aria-label="Primary navigation"><button v-if="authed" class="rd-nav" :class="{active:view==='start'}" :aria-current="(view==='start')?'page':null" @click="go('start')">{{t('nav.getting_started')}}</button>
<button v-if="canRegister" class="rd-nav" :class="{active:view==='catalog'}" :aria-current="(view==='catalog')?'page':null" @click="go('catalog')">{{t('nav.catalog')}}</button>
<button v-if="authed" class="rd-nav" :class="{active:view==='connections'||view==='provider'}" :aria-current="(view==='connections'||view==='provider')?'page':null" @click="go('connections')">{{t('nav.connections')}}</button>
<button v-if="authed" class="rd-nav" :class="{active:view==='tools'||view==='secrets'||view==='resources'}" :aria-current="(view==='tools'||view==='secrets'||view==='resources')?'page':null" @click="go('tools')">{{t('nav.your_tools')}}</button>
<button v-if="authed" class="rd-nav" :class="{active:view==='activity'}" :aria-current="(view==='activity')?'page':null" @click="go('activity')">{{t('nav.activity')}}</button>
<button v-if="authed && hubOn" class="rd-nav" :class="{active:view==='hub'||view==='run'}" :aria-current="(view==='hub'||view==='run')?'page':null" @click="go('hub')">{{t('nav.hub')}}</button>
<button v-if="authed" class="rd-nav" :class="{active:view==='orgs'}" :aria-current="(view==='orgs')?'page':null" @click="go('orgs')">{{t('nav.team')}}</button>
<button v-if="authed" class="rd-nav" style="color:var(--accent, #10b981);font-weight:600" @click="agentConnectDialog=true">{{t('mcp.nav_btn')}}</button></nav>
      <div class="rd-account">
        <LangSwitch style="margin-right:8px" />
        <a v-if="authed" class="rd-referral" href="#referrals" @click.prevent="go('referrals')" :aria-current="view==='referrals'?'page':null" :title="refEntryTitle()" :aria-label="'Referral: '+refEntryTitle()"><img src="/media/redesign/referral-gift.svg" alt=""><span>{{t('nav.referral')}}</span></a>
        <button v-if="billing" class="rd-balance" :title="'Balance: '+money(billing.balance_micro)" @click="orgTab='billing'; go('orgs')"><span>{{t('nav.balance')}}</span><b>{{moneyGlance(billing.balance_micro)}}</b></button>
        <details class="rd-account-menu" :ref="el => setElement('accountMenu', el)">
          <summary :aria-label="'Account: '+me"><span class="rd-avatar" style="overflow:hidden"><img v-if="meAvatar && !meAvatarBroken" :src="meAvatar" alt="" style="width:100%;height:100%;object-fit:cover" @error="meAvatarBroken=true"><template v-else>{{initials}}</template></span></summary>
          <div class="rd-account-panel">
            <p class="rd-email">{{me}}</p>
            <button @click="agentConnectDialog=true; elements.accountMenu.open=false" style="font-weight:600;color:var(--accent, #10b981)">{{t('mcp.nav_btn')}}</button>
            <button @click="avatarDialog=true; elements.accountMenu.open=false">{{t('nav.your_avatar')}}</button>
            <button @click="changePasswordDialog=true; elements.accountMenu.open=false">{{t('nav.change_password')}}</button>
            <button @click="toggleTheme">{{theme==='dark'?t('nav.theme_light'):t('nav.theme_dark')}}</button>
            <button v-if="billing" @click="orgTab='billing'; go('orgs'); elements.accountMenu.open=false">{{t('nav.billing')}}</button>
            <button v-if="isAdmin" @click="go('admin'); elements.accountMenu.open=false">{{t('nav.admin')}}</button>
            <a href="/tutorial">{{t('nav.tutorial')}}</a>
            <a href="https://github.com/superdesigndev/treg" target="_blank" rel="noopener">GitHub</a>
            <a href="https://discord.gg/6mQYYfFMAn" target="_blank" rel="noopener">Discord</a>
            <a href="https://x.com/treg_ai" target="_blank" rel="noopener">Follow on X</a>
            <button @click="logout">{{t('nav.signout')}}</button>
          </div>
        </details>
      </div>
    </header>
</template>
