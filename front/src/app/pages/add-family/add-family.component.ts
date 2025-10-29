import { Component, OnInit, ViewChild, ElementRef, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { LanguageService } from '../../languagesService';
import { TranslateAddFamilyService } from '../../translate-add-family.service';
import { environment } from '../../../environments/environment';
import { response } from 'express';

@Component({
  selector: 'app-add-family',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './add-family.component.html',
  styleUrls: ['./add-family.component.css']
})
export class AddFamilyComponent implements OnInit {
  @ViewChild('commentTextarea') commentTextarea!: ElementRef<HTMLTextAreaElement>;
  
  dbName: string = '';
  currentTab: 'parents' | 'events' | 'children' | 'sources' | 'comments' = 'parents';
  currentLanguage = 'FR';
  showLanguageDropdown = false;
  token = '';

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

  // Parent (H) - Homme
  parentH = {
    firstName: '',
    lastName: '',
    birthDay: '',
    birthMonth: '',
    birthYear: '',
    birthPlace: '',
    deathDay: '',
    deathMonth: '',
    deathYear: '',
    deathPlace: '',
    profession: '',
    number: '0'
  };

  // Parent (F) - Femme
  parentF = {
    firstName: '',
    lastName: '',
    birthDay: '',
    birthMonth: '',
    birthYear: '',
    birthPlace: '',
    deathDay: '',
    deathMonth: '',
    deathYear: '',
    deathPlace: '',
    profession: '',
    number: '0'
  };

  homosexualRelation = false;

  // Events
  events: any[] = [];
  
  // Children
  children: any[] = [];

  // Sources
  personSources = '';
  familySources = '';

  // Comments
  comment = '';

  // Menu visibility states
  showHtmlMenu = false;
  showH1Menu = false;
  showFormatMenu = false;
  showListMenu = false;
  showNotesMenu = false;
  showSommaireMenu = false;
  showPersonneMenu = false;

  // HTML templates
  htmlTemplates = [
    { label: '<br/>', value: '<br/>' },
    { label: '<hr/> (––––––––)', value: '<hr/>' },
    { label: '<table>', value: '<table border>\n<tr>\n<th>A1</th>\n<th>B1</th>\n</tr><tr>\n<td>A2</td>\n<td>B2</td>\n</tr><tr>\n<td>A3</td>\n<td>B3</td>\n</tr>\n</table>' },
    { label: '<img alt="?" src="%sm=IM;s=xxx.jpg"/>', value: '<img src="%sm=IM;s=xxx.jpg"/> alt="?"' },
    { label: '<a href="%sm=IMH;s=xxx.jpg">image</a>', value: '<a href="%sm=IMH;s=xxx.jpg">Image</a>' }
  ];

  // H1-H6 templates
  h1Templates = [
    { label: '=h1=', value: '=x=' },
    { label: '==h2==', value: '==x==' },
    { label: '===h3===', value: '===x===' },
    { label: '====h4====', value: '====x====' },
    { label: '=====h5=====', value: '=====x=====' },
    { label: '======h6======', value: '======x======' }
  ];

  // Format templates
  formatTemplates = [
    { label: 'Italic', value: "''x''" },
    { label: 'Bold', value: "'''x'''" },
    { label: 'Underline', value: '__x__' },
    { label: 'Strike', value: '~~x~~' },
    { label: 'Highlight', value: '{x}' }
  ];

  // List templates
  listTemplates = [
    { label: '• *ul li', value: '*\n' },
    { label: '• **ul ul li', value: '**\n' },
    { label: '1. #ol li', value: '#\n' },
    { label: '2. ##ol ol li', value: '##\n' },
    { label: ';dl dt:dd', value: ';x:x\n' },
    { label: ':dl dd', value: ':\n' },
    { label: '::dl dl dd', value: '::\n' },
    { label: 'pre', value: '\n\n' },
    { label: 'pre', value: '\n\n' }
  ];

  // Notes diverses templates
  notesTemplates = [
    { label: '[[[directory:filename/texte]]]', value: '[[[x:x/x]]]' },
    { label: 'TITLE=', value: 'TITLE=' },
    { label: 'HEAD=lui/elle', value: 'HEAD=' },
    { label: 'DEATH=', value: 'DEATH=' },
    { label: 'OCCU=', value: 'OCCU=' },
    { label: 'BNOTE=', value: 'BNOTE=' },
    { label: 'NOTE=', value: 'NOTE=' },
    { label: 'BIBLIO=', value: 'BIBLIO=' }
  ];

  // Sommaire templates
  sommaireTemplates = [
    { label: '__TOC__', value: '__TOC__' },
    { label: '__SHORT_TOC__', value: '__SHORT_TOC__' },
    { label: '__NOTOC__', value: '__NOTOC__' }
  ];

  // Personne templates
  personneTemplates = [
    { label: '[[w:magicien]]', value: '[[w:x]]' },
    { label: '[[prénom/patronyme]]', value: '[[x/x]]' },
    { label: '[[prénom/patronyme/numéro/ texte href]]', value: '[[x/x/x/x]]' },
    { label: '[[prénom/patronyme/numéro/ texte href; personne texte href]]', value: '[[x/x/x/x;x]]' }
  ];

  // Special characters for comment section
  specialChars = [
    '–', '—', '«', '»', '\u2018', '\u2019', '\u201C', '\u201D',
    'Á', 'á', 'À', 'à', 'Ã', 'ã', 'Â', 'â', 'Ä', 'ä', 'Ǎ', 'ǎ', 'Ă', 'ă',
    'Ā', 'ā', 'Ą', 'ą', 'Å', 'å', 'Æ', 'æ', 'Ǣ', 'ǣ',
    'É', 'é', 'È', 'è', 'Ê', 'ê', 'Ë', 'ë', 'Ě', 'ě', 'Ė', 'ė', 'Ē', 'ē',
    'Ę', 'ę', 'Ə', 'ə', 'Σ', 'ʃ',
    'Í', 'í', 'Ì', 'ì', 'Î', 'î', 'Ï', 'ï', 'Ǐ', 'ǐ', 'Ĭ', 'ĭ', 'Ī', 'ī', 'Į', 'į',
    'İ', 'Ù', 'ù', 'Ij', 'ij',
    'Ó', 'ó', 'Ò', 'ò', 'Õ', 'õ', 'Ô', 'ô', 'Ö', 'ö', 'Ǒ', 'ǒ', 'Ŏ', 'ŏ', 'Ō', 'ō',
    'Ő', 'ő', 'Ø', 'ø', 'Œ', 'œ', 'Ǿ', 'ǿ',
    'Ú', 'ú', 'Ù', 'ù', 'Ũ', 'ũ', 'Û', 'û', 'Ü', 'ü', 'Ǔ', 'ǔ', 'Ŭ', 'ŭ', 'Ū', 'ū',
    'Ű', 'ű', 'Ů', 'ů', 'Ų', 'ų',
    'Ý', 'ý', 'Ỳ', 'ỳ', 'Ỹ', 'ỹ', 'Ŷ', 'ŷ', 'Ÿ', 'ÿ', 'Ȳ', 'ȳ', 'Ɏ', 'ɏ',
    'Ć', 'ć', 'Ĉ', 'ĉ', 'Č', 'č', 'Ç', 'ç', 'Ď', 'ď', 'Đ', 'đ', 'Ð', 'ð', 'Ñ', 'ñ', 'Ň', 'ň',
    'Ŋ', 'ŋ',
    'Ŕ', 'ŕ', 'Ř', 'ř', 'Ś', 'ś', 'Ŝ', 'ŝ', 'Š', 'š', 'Ş', 'ş', 'ẞ', 'ß',
    'Ť', 'ť', 'Ŧ', 'ŧ', 'Þ', 'þ', 'Ź', 'ź', 'Ż', 'ż', 'Ž', 'ž', 'Ʒ', 'ʒ',
    '¹', '²', '³', '½', '⅓', '¾', '°', 'ª',
    '¡', '¿', '•', '·', '×', '÷', '€', '£', '℥', '©', '®', '℗', 'µ',
    '¶', '§', '†', '‡', '№'
  ];

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient,
    public languageService: LanguageService,
    public translate: TranslateAddFamilyService
  ) {
    // Initialize current language display
    const currentLang = this.languageService.getLang();
    this.currentLanguage = currentLang.toUpperCase();
    this.token = localStorage.getItem('auth_token') || '';
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.dbName = params['dbName'] || 'Test';
    });
  }

  // Close dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.language-dropdown')) {
      this.showLanguageDropdown = false;
    }
  }

  scrollToSection(section: string) {
    const element = document.getElementById(section);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      
      // Update active tab based on section
      if (section === 'parents-section') this.currentTab = 'parents';
      else if (section === 'events-section') this.currentTab = 'events';
      else if (section === 'children-section') this.currentTab = 'children';
      else if (section === 'sources-section') this.currentTab = 'sources';
      else if (section === 'comments-section') this.currentTab = 'comments';
    }
  }

  addEvent(count: number, isWitness: boolean) {
    for (let i = 0; i < count; i++) {
      this.events.push({
        type: '',
        place: '',
        day: '',
        month: '',
        year: '',
        exactDate: 'exact',
        dateType: '-',
        secondDay: '',
        secondMonth: '',
        secondYear: '',
        textDate: '',
        notes: '',
        source: '',
        isWitness: isWitness
      });
    }
  }

  addChild(count: number) {
    for (let i = 0; i < count; i++) {
      this.children.push({
        action: 'create',
        firstName: '',
        lastName: '',
        number: '0',
        sex: '?',
        birthDay: '',
        birthMonth: '',
        birthYear: '',
        birthPlace: '',
        deathDay: '',
        deathMonth: '',
        deathYear: '',
        deathPlace: '',
        profession: ''
      });
    }
  }

  removeEvent(index: number) {
    this.events.splice(index, 1);
  }

  removeChild(index: number) {
    this.children.splice(index, 1);
  }

  saveParents() {
    const apiUrl = `${environment.apiUrl}`;
    
    // Helper function to format date from day, month, year
    const formatDate = (day: string, month: string, year: string): string | null => {
      if (!year) return null;
      const y = year.padStart(4, '0');
      const m = month ? month.padStart(2, '0') : '01';
      const d = day ? day.padStart(2, '0') : '01';
      return `${y}-${m}-${d}`;
    };

    // Validate that at least one parent has data
    const hasParentH = this.parentH.firstName || this.parentH.lastName;
    const hasParentF = this.parentF.firstName || this.parentF.lastName;

    if (!hasParentH && !hasParentF) {
      alert('Veuillez renseigner au moins un parent (prénom ou nom).');
      return;
    }

    const headers = {
      'Authorization': `Bearer ${this.token}`
    };

    const promises: Promise<any>[] = [];

    // Create parent H if data exists
    if (hasParentH) {
      const parentHData = {
        first_name: this.parentH.firstName || '',
        last_name: this.parentH.lastName || '',
        sex: 'male',
        birth_date: formatDate(this.parentH.birthDay, this.parentH.birthMonth, this.parentH.birthYear),
        birth_place: this.parentH.birthPlace || '',
        death_date: formatDate(this.parentH.deathDay, this.parentH.deathMonth, this.parentH.deathYear),
        death_place: this.parentH.deathPlace || '',
        occupation: this.parentH.profession || ''
      };

      promises.push(
        this.http.post<any>(`${apiUrl}/persons/`, parentHData, { headers: headers }).toPromise()
          .then(response => {
            console.log('Parent H created:', response);
            return response;
          })
          .catch(error => {
            console.error('Error creating parent H:', error);
            throw error;
          })
      );
    }

    // Create parent F if data exists
    if (hasParentF) {
      const parentFData = {
        first_name: this.parentF.firstName || '',
        last_name: this.parentF.lastName || '',
        sex: 'female',
        birth_date: formatDate(this.parentF.birthDay, this.parentF.birthMonth, this.parentF.birthYear),
        birth_place: this.parentF.birthPlace || '',
        death_date: formatDate(this.parentF.deathDay, this.parentF.deathMonth, this.parentF.deathYear),
        death_place: this.parentF.deathPlace || '',
        occupation: this.parentF.profession || ''
      };

      promises.push(
        this.http.post<any>(`${apiUrl}/persons/`, parentFData, { headers: headers }).toPromise()
          .then(response => {
            console.log('Parent F created:', response);
            return response;
          })
          .catch(error => {
            console.error('Error creating parent F:', error);
            throw error;
          })
      );
    }

    // Execute all promises
    Promise.all(promises)
      .then(responses => {
        alert(`Parent(s) enregistré(s) avec succès ! ${responses.length} personne(s) créée(s).`);
        // Optionally, you could store the person IDs for later use
        console.log('All parents saved:', responses);
      })
      .catch(error => {
        alert('Erreur lors de l\'enregistrement des parents. Voir la console pour plus de détails.');
        console.error('Error saving parents:', error);
      });
  }

  onSubmit() {
      const apiUrl = `${environment.apiUrl}`;
      
    // Helper function to format date from day, month, year
    const formatDate = (day: string, month: string, year: string): string | null => {
      if (!year) return null;
      const y = year.padStart(4, '0');
      const m = month ? month.padStart(2, '0') : '01';
      const d = day ? day.padStart(2, '0') : '01';
      return `${y}-${m}-${d}`;
    };

    // Helper function to determine sex
    const getSex = (firstName: string): string => {
      // This is a simple heuristic, you may want to add a proper field or logic
      return 'unknown';
    };

    // Create parent H (Father/Parent 1)
    const createParentH = async () => {
      const parentHId: string[] = [];
      if (!this.parentH.firstName && !this.parentH.lastName) {
        return Promise.resolve(null);
      }

      const parentHData = {
        first_name: this.parentH.firstName || '',
        last_name: this.parentH.lastName || '',
        sex: 'male', // Assuming H is male
        birth_date: formatDate(this.parentH.birthDay, this.parentH.birthMonth, this.parentH.birthYear),
        birth_place: this.parentH.birthPlace || '',
        death_date: formatDate(this.parentH.deathDay, this.parentH.deathMonth, this.parentH.deathYear),
        death_place: this.parentH.deathPlace || '',
        occupation: this.parentH.profession || ''
      };

      const headers = {
        'Authorization': `Bearer ${this.token}`
      };
      let response = null;

      try {
        response = await this.http.post<any>(`${apiUrl}/persons`, parentHData, { headers }).toPromise();
        if (response && response.person_id) parentHId.push(response.person_id);
      } catch (error) {
        console.error('Error creating parent H:', error);
        throw error;
      }
      return response;
    };

    // Create parent F (Mother/Parent 2)
    const createParentF = async () => {
      const parentFId: string[] = [];
      if (!this.parentF.firstName && !this.parentF.lastName) {
        return Promise.resolve(null);
      }

      const parentFData = {
        first_name: this.parentF.firstName || '',
        last_name: this.parentF.lastName || '',
        sex: 'female', // Assuming F is female
        birth_date: formatDate(this.parentF.birthDay, this.parentF.birthMonth, this.parentF.birthYear),
        birth_place: this.parentF.birthPlace || '',
        death_date: formatDate(this.parentF.deathDay, this.parentF.deathMonth, this.parentF.deathYear),
        death_place: this.parentF.deathPlace || '',
        occupation: this.parentF.profession || ''
      };

      const headers = {
        'Authorization': `Bearer ${this.token}`
      };

      let response = null;

      try {
        response = await this.http.post<any>(`${apiUrl}/persons`, parentFData, { headers }).toPromise();
        if (response && response.person_id) parentFId.push(response.person_id);
      } catch (error) {
        console.error('Error creating parent F:', error);
        throw error;
      }
      return response;
    };

    // Create children
    const createChildren = async () => {
      const childrenIds: string[] = [];
      
      for (const child of this.children) {
        if (!child.firstName && !child.lastName) continue;

        const childData = {
          first_name: child.firstName || '',
          last_name: child.lastName || '',
          sex: child.sex === 'M' ? 'male' : child.sex === 'F' ? 'female' : 'unknown',
          birth_date: formatDate(child.birthDay, child.birthMonth, child.birthYear),
          birth_place: child.birthPlace || '',
          death_date: formatDate(child.deathDay, child.deathMonth, child.deathYear),
          death_place: child.deathPlace || '',
          occupation: child.profession || ''
        };

        const headers = {
          'Authorization': `Bearer ${this.token}`
        };

        try {
          const response = await this.http.post<any>(`${apiUrl}/persons`, childData, { headers }).toPromise();
          if (response && response.person_id) {
            childrenIds.push(response.person_id);
          }
        } catch (error) {
          console.error('Error creating child:', error);
        }
      }

      return childrenIds;
    };

    // Main submission logic
    Promise.all([createParentH(), createParentF()])
      .then(async ([parentHResponse, parentFResponse]) => {
        const fatherIds = parentHResponse?.id ? [parentHResponse.id] : [];
        const motherIds = parentFResponse?.id ? [parentFResponse.id] : [];
        const childrenIds = await createChildren();

        // Determine relation type
        let relation = 'married'; // Default
        if (this.events.some(e => e.type === 'Fiançailles')) {
          relation = 'engaged';
        } else if (this.events.some(e => e.type === 'PACS')) {
          relation = 'pacs';
        } else if (this.events.some(e => e.type === 'Ne se sont pas mariés')) {
          relation = 'no_sexes_mention';
        }

        // Find marriage event for date/place
        const marriageEvent = this.events.find(e => e.type === 'Mariage' || e.type === 'Marriage');
        const marriageDate = marriageEvent ? formatDate(marriageEvent.day, marriageEvent.month, marriageEvent.year) : null;
        const marriagePlace = marriageEvent?.place || '';
        const marriageSource = marriageEvent?.source || this.familySources || '';

        // Map events to API format
        const apiEvents = this.events.map(event => {
          const eventDate = formatDate(event.day, event.month, event.year);
          
          return {
            event_name: event.type?.toLowerCase().replace(/\s+/g, '_') || 'custom',
            custom_name: event.type || null,
            date: eventDate,
            place: event.place || '',
            note: event.notes || '',
            source: event.source || '',
            reason: '',
            witnesses: [] // You can add witness mapping here if needed
          };
        });

        // Create family
        const familyData = {
          father_ids: fatherIds,
          mother_ids: motherIds,
          children_ids: childrenIds,
          relation: relation,
          marriage_date: marriageDate,
          marriage_place: marriagePlace,
          marriage_source: marriageSource,
          divorce_info: {
            divorce_status: 'not_divorced',
            divorce_date: null
          },
          comment: this.comment || '',
          events: apiEvents
        };

        const headers = {
          'Authorization': `Bearer ${this.token}`
        };

        return this.http.post<any>(`${apiUrl}/families`, familyData, { headers }).toPromise();
      })
      .then(familyResponse => {
        console.log('Family created successfully:', familyResponse);
        alert('Famille ajoutée avec succès !');
        this.router.navigate(['/database', this.dbName]);
      })
      .catch(error => {
        console.error('Error creating family:', error);
        alert('Erreur lors de l\'ajout de la famille. Voir la console pour plus de détails.');
      });
  }

  goBack() {
    this.router.navigate(['/database', this.dbName]);
  }

  insertChar(char: string) {
    const textarea = this.commentTextarea?.nativeElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = this.comment;
      
      // Insert character at cursor position
      this.comment = text.substring(0, start) + char + text.substring(end);
      
      // Set cursor position after inserted character
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + char.length;
        textarea.focus();
      }, 0);
    } else {
      // Fallback if textarea is not available
      this.comment += char;
    }
  }

  toggleMenu(menu: string) {
    // Close all menus first
    this.showHtmlMenu = false;
    this.showH1Menu = false;
    this.showFormatMenu = false;
    this.showListMenu = false;
    this.showNotesMenu = false;
    this.showSommaireMenu = false;
    this.showPersonneMenu = false;

    // Open the selected menu
    switch(menu) {
      case 'html':
        this.showHtmlMenu = true;
        break;
      case 'h1':
        this.showH1Menu = true;
        break;
      case 'format':
        this.showFormatMenu = true;
        break;
      case 'list':
        this.showListMenu = true;
        break;
      case 'notes':
        this.showNotesMenu = true;
        break;
      case 'sommaire':
        this.showSommaireMenu = true;
        break;
      case 'personne':
        this.showPersonneMenu = true;
        break;
    }
  }

  insertTemplate(template: string) {
    this.insertChar(template);
    // Close all menus after insertion
    this.showHtmlMenu = false;
    this.showH1Menu = false;
    this.showFormatMenu = false;
    this.showListMenu = false;
    this.showNotesMenu = false;
    this.showSommaireMenu = false;
    this.showPersonneMenu = false;
  }

  toggleLanguageDropdown() {
    this.showLanguageDropdown = !this.showLanguageDropdown;
  }

  changeLanguage(lang: string) {
    this.currentLanguage = lang.toUpperCase();
    this.languageService.setLang(lang);
    this.translate.setLang(lang);
    this.showLanguageDropdown = false;
  }
}
