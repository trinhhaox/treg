<script>
import { useDashboard } from '../state/context'
import { t } from '../state/i18n'
import OwnToolsHeader from '../components/OwnToolsHeader.vue'
import LoadFromMachine from '../components/LoadFromMachine.vue'
import { DataTable } from '../components/ui/table'

export default {
  components: { OwnToolsHeader, LoadFromMachine, DataTable },
  setup: useDashboard,
  computed: {
    columns() {
      return [
        { key: 'name', header: t('secrets.col_name'), mobile: 'primary' },
        { key: 'kind', header: t('secrets.col_kind') },
        { key: 'owner', header: t('secrets.col_added_by') },
        { key: 'acts', header: '', align: 'right' },
      ]
    }
  }
}
</script>

<template>
<div class="pl own">
  <OwnToolsHeader current="secrets">
    {{t('secrets.desc')}}
    {{t('secrets.connections_link')}}: <a href="#connections" @click.prevent="go('connections')">{{t('conn.title')}}</a><template v-if="secrets.length>ownSecrets.length"> ({{secrets.length-ownSecrets.length}})</template>.
  </OwnToolsHeader>

  <div v-if="orgMsg" class="banner cn-banner"><span>{{orgMsg}}</span><button class="btn sm ico" @click="orgMsg=''" aria-label="Dismiss">✕</button></div>
  <div v-if="secretErr" class="banner err cn-banner"><span>{{secretErr}}</span><button class="btn sm ico" @click="secretErr=''" aria-label="Dismiss">✕</button></div>

  <section v-if="ownSecrets.length" class="pl-sec">
    <h2 class="pl-h"><span>{{t('secrets.title')}}</span><i></i><em>{{ownSecrets.length}}</em></h2>
    <DataTable :columns="columns" :rows="ownSecrets" :row-key="s => String(s.id)" surface>
      <template #cell-name="{ row: s }"><b class="mono">{{s.name}}</b></template>
      <template #cell-kind="{ row: s }"><span class="muted">{{s.kind}}</span></template>
      <template #cell-owner="{ row: s }"><span class="muted">{{s.owner ? short(s.owner) : '-'}}</span></template>
      <template #cell-acts="{ row: s }"><span class="cn-links"><button class="cn-del" :class="{armed:confirmDelSecret===s.id}" @click="deleteSecret(s)">
        {{confirmDelSecret===s.id ? t('secrets.delete_confirm') : t('common.delete')}}</button></span></template>
    </DataTable>
  </section>

  <section class="pl-sec">
    <h2 class="pl-h"><span>{{t('secrets.add_title')}}</span><i></i></h2>
    <div class="pl-card own-form">
      <p class="own-form-tip">{{t('secrets.tip_env')}}</p>
          <div v-for="(row,i) in secretRows" :key="i" class="field" style="flex-wrap:wrap;margin-bottom:8px">
            <input v-model="row.name" :placeholder="t('secrets.name_ph')" style="min-width:150px" @paste="pasteEnv($event,i,'name')" @keyup.enter="addSecrets"/>
            <input v-model="row.value" :type="row.kind==='param'?'text':'password'" :placeholder="row.kind==='param'?t('secrets.val_ph_param'):t('secrets.val_ph_secret')" style="min-width:190px" @paste="pasteEnv($event,i,'value')" @keyup.enter="addSecrets"/>
            <select v-model="row.kind" class="msel"><option>env</option><option>oauth</option><option>secret_file</option><option value="param">param</option></select>
            <button v-if="secretRows.length>1" class="btn sm ico" @click="secretRows.splice(i,1)" title="Remove row">✕</button>
            <span v-if="secretNameHint(row)" class="sub" style="flex-basis:100%;font-size:11.5px;margin:-2px 0 0">
              <template v-if="secretNameHint(row).ok">✓ {{secretNameHint(row).text}}</template>
              <template v-else>{{secretNameHint(row).text}}
                <a href="#" @click.prevent="row.name=secretNameHint(row).service">rename to “{{secretNameHint(row).service}}”</a></template>
            </span>
          </div>
      <div class="own-form-a">
        <button class="pl-btn" @click="addSecrets" :disabled="secretBusy||!secretRowsReady">{{secretBusy?'…':(secretRowsReady>1?t('secrets.add_multi_btn', {n: secretRowsReady}):t('secrets.add_btn'))}}</button>
        <button class="pl-btn ghost" @click="secretRows.push({name:'',value:'',kind:'env'})">{{t('secrets.another_row')}}</button>
        <button v-if="secretRows.length>1" class="pl-btn ghost" @click="secretRows=[{name:'',value:'',kind:'env'}]">{{t('secrets.clear')}}</button>
      </div>
    </div>
  </section>

  <LoadFromMachine v-if="!ownSecrets.length" :title="t('secrets.load_bulk')">
    Bulk-load your keys (and skills): each lands here encrypted, referenced by name.
  </LoadFromMachine>
</div>
</template>
