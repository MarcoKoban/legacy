import { Component, HostListener, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { LanguageService } from '../../languagesService';
import { TranslateConfigurationService } from '../../translate-configuration.service';
import gitInfo from '../../../assets/git-info.json';

@Component({
  selector: 'app-configuration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css']
})
export class ConfigurationComponent implements OnInit {
  dbName: string = '';
  currentLanguage = 'FR';
  showLanguageDropdown = false;

  // Build information
  genewebVersion = '7.1-beta';
  branchName = gitInfo.branch;
  compilationDate = gitInfo.commitDate;
  commitId = gitInfo.commitId;

  // User and language variables
  userIdent = 'username';
  userName = '';
  userKey = '';
  langFull = 'français (fr)';
  langCode = 'fr';
  langFallback = 'en';
  defaultLang = 'en';
  browserLang = 'en';

  // Gwd arguments
  gwdArglist = 'make run-api';
  isCGI = false;
  prefix = '';
  etcPrefix = '';
  imagesPrefix = 'images/';

  // Configuration parameters
  isReorg = false;
  configFile = '';
  bvarList: string[] = [];
  
  // Additional configuration parameters
  configParams = {
    access_by_key: 'yes',
    disable_forum: 'yes',
    hide_private_names: 'no',
    use_restrict: 'no',
    show_consang: 'yes',
    display_sosa: 'yes',
    place_surname_link_to_ind: 'yes',
    max_anc_level: '8',
    max_anc_tree: '7',
    max_desc_level: '12',
    max_desc_tree: '4',
    max_cousins: '2000',
    max_cousins_level: '5',
    latest_event: '20',
    template: '*',
    long_date: 'no',
    counter: 'no',
    full_siblings: 'yes',
    hide_advanced_request: 'no',
    p_mod: ''
  };

  // List of supported languages
  languages = [
    { code: 'co', label: 'Corsu' },
    { code: 'de', label: 'Deutsch' },
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Español' },
    { code: 'fr', label: 'Français' },
    { code: 'it', label: 'Italiano' },
    { code: 'lv', label: 'Latviešu' },
    { code: 'sv', label: 'Svenska' },
    { code: 'fi', label: 'Suomi' },
  ];

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private location: Location,
    public languageService: LanguageService,
    public translate: TranslateConfigurationService
  ) {
    // Initialize current language display
    const currentLang = this.languageService.getLang();
    this.currentLanguage = currentLang.toUpperCase();
    this.translate.setLang(currentLang);
  }

  ngOnInit() {
    // Récupérer le nom de la base de données depuis les paramètres de route
    this.route.params.subscribe(params => {
      const dbName = params['dbName'];
      if (dbName) {
        this.dbName = dbName;
        this.configFile = `${dbName}.gwf`;
        this.prefix = `${dbName}?lang=${this.langCode}&`;
      } else {
        this.prefix = 'base?lang=fr&';
      }
      
      // Update bvarList with current values
      this.updateBvarList();
    });

    // Update language variables based on current language
    this.updateLanguageVariables();
  }

  updateBvarList() {
    this.bvarList = [
      '-blang',
      '-log geneweb_python/logs/api.log',
      `Mode: ${this.isCGI ? 'CGI' : 'Server'}`,
      `prefix: ${this.prefix}`,
      `etc_prefix: ${this.etcPrefix || '-'}`,
      `images_prefix: ${this.imagesPrefix}`
    ];
  }

  updateLanguageVariables() {
    const lang = this.languageService.getLang();
    this.langCode = lang;
    
    const langLabels: { [key: string]: string } = {
      'fr': 'français (fr)',
      'en': 'english (en)',
      'de': 'deutsch (de)',
      'es': 'español (es)',
      'it': 'italiano (it)',
      'co': 'corsu (co)',
      'lv': 'latviešu (lv)',
      'sv': 'svenska (sv)',
      'fi': 'suomi (fi)'
    };
    
    this.langFull = langLabels[lang] || 'français (fr)';
  }

  // Close dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.language-dropdown')) {
      this.showLanguageDropdown = false;
    }
  }

  toggleLanguageDropdown() {
    this.showLanguageDropdown = !this.showLanguageDropdown;
  }

  changeLanguage(lang: string) {
    this.currentLanguage = lang.toUpperCase();
    this.languageService.setLang(lang);
    this.translate.setLang(lang);
    this.updateLanguageVariables();
    
    // Update prefix with new language
    if (this.dbName) {
      this.prefix = `${this.dbName}?lang=${lang}&`;
    } else {
      this.prefix = `base?lang=${lang}&`;
    }
    this.updateBvarList();
    
    this.showLanguageDropdown = false;
  }

  goBack() {
    this.location.back();
  }

  goHome() {
    if (this.dbName) {
      this.router.navigate(['/database', this.dbName]);
    } else {
      this.router.navigate(['/']);
    }
  }
}
